-- ============================================
-- AKIRA TRADERS - SUPABASE SCHEMA v2.0
-- ============================================
-- Ejecutar este SQL en el SQL Editor de Supabase
-- https://supabase.com/dashboard/project/YOUR_PROJECT/sql
--
-- IMPORTANTE: Ejecutar en orden (las tablas tienen dependencias)
-- ============================================

-- ============================================
-- LIMPIEZA (solo para desarrollo, comentar en producción)
-- ============================================
-- DROP VIEW IF EXISTS v_evaluations_summary;
-- DROP VIEW IF EXISTS v_trader_stats;
-- DROP TABLE IF EXISTS evaluations CASCADE;
-- DROP TABLE IF EXISTS traders CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column();

-- ============================================
-- EXTENSIONES
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- FUNCIÓN: Actualizar updated_at automáticamente
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TABLA: traders
-- ============================================
-- Catálogo de traders de Binance Copy Trading
-- Compartido entre todos los usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS traders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Identificación
    display_name TEXT NOT NULL,
    binance_uid TEXT UNIQUE,                    -- ID único de Binance (si disponible)
    binance_profile_url TEXT,                   -- URL del perfil

    -- Clasificación
    trading_style TEXT CHECK (trading_style IN (
        'scalping',
        'swing',
        'trend-following',
        'arbitrage',
        'mixed'
    )),

    -- Metadata
    notes TEXT,
    tags TEXT[],                                -- Tags personalizados: ['top-performer', 'low-risk', etc.]

    -- Estado
    is_active BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT traders_display_name_not_empty CHECK (LENGTH(TRIM(display_name)) > 0)
);

-- Índices para traders
CREATE INDEX IF NOT EXISTS idx_traders_display_name ON traders(display_name);
CREATE INDEX IF NOT EXISTS idx_traders_style ON traders(trading_style);
CREATE INDEX IF NOT EXISTS idx_traders_active ON traders(is_active);
CREATE INDEX IF NOT EXISTS idx_traders_binance_uid ON traders(binance_uid);
CREATE INDEX IF NOT EXISTS idx_traders_tags ON traders USING GIN(tags);

-- Trigger para updated_at
DROP TRIGGER IF EXISTS trg_traders_updated_at ON traders;
CREATE TRIGGER trg_traders_updated_at
    BEFORE UPDATE ON traders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- TABLA: evaluations
-- ============================================
-- Evaluaciones de traders por usuario
-- Cada usuario puede tener múltiples evaluaciones del mismo trader
-- ============================================
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Relaciones
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    trader_id UUID REFERENCES traders(id) ON DELETE CASCADE NOT NULL,

    -- Contexto de la evaluación
    evaluated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,     -- Fecha/hora de la evaluación

    -- Perfil de riesgo usado para evaluar
    risk_profile TEXT NOT NULL CHECK (risk_profile IN (
        'conservative',
        'moderate',
        'aggressive'
    )),

    -- Criterios de selección aplicados
    selection_criteria JSONB NOT NULL DEFAULT '{}'::JSONB,
    /*
    Estructura esperada:
    {
        "roi_90d_range_pct": [20, 60],
        "max_drawdown_pct_lte": 20,
        "win_rate_pct_gte": 55,
        "min_days_active": 90,
        "leverage_range": [1, 3],
        "min_copiers": 100
    }
    */

    -- Métricas capturadas (snapshot del momento)
    metrics JSONB NOT NULL DEFAULT '{}'::JSONB,
    /*
    Estructura esperada:
    {
        "roi_30d_pct": 15.5,
        "roi_90d_pct": 42.3,
        "roi_180d_pct": null,
        "max_drawdown_pct": 8.2,
        "win_rate_pct": 65,
        "avg_leverage": 2.1,
        "copiers": 1250,
        "days_active": 180
    }
    */

    -- Configuración de copia sugerida
    copy_settings JSONB DEFAULT '{}'::JSONB,
    /*
    Estructura esperada:
    {
        "copy_mode": "fixed",           -- 'fixed' | 'ratio'
        "order_size_usdt": 50,          -- Mínimo 10 USDT
        "daily_loss_cap_pct": 5,
        "stop_copy_drawdown_pct": 15,
        "assets_whitelist": ["BTC", "ETH", "BNB"]
    }
    */

    -- Resultado de la evaluación
    decision TEXT CHECK (decision IN (
        'approved',     -- Cumple criterios, recomendado copiar
        'rejected',     -- No cumple criterios
        'watchlist'     -- Monitorear, potencial futuro
    )),

    -- Scoring calculado
    total_score NUMERIC(5,2),            -- Score total (0-100)

    -- Notas del evaluador
    notes TEXT,

    -- Constraint único: evitar duplicados exactos
    CONSTRAINT evaluations_unique_evaluation
        UNIQUE(user_id, trader_id, evaluated_at)
);

-- Índices para evaluations
CREATE INDEX IF NOT EXISTS idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_trader_id ON evaluations(trader_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluated_at ON evaluations(evaluated_at DESC);
CREATE INDEX IF NOT EXISTS idx_evaluations_risk_profile ON evaluations(risk_profile);
CREATE INDEX IF NOT EXISTS idx_evaluations_decision ON evaluations(decision);
CREATE INDEX IF NOT EXISTS idx_evaluations_score ON evaluations(total_score DESC NULLS LAST);

-- Índices GIN para búsquedas en JSONB
CREATE INDEX IF NOT EXISTS idx_evaluations_metrics_gin ON evaluations USING GIN(metrics);
CREATE INDEX IF NOT EXISTS idx_evaluations_criteria_gin ON evaluations USING GIN(selection_criteria);

-- Índice compuesto para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_evaluations_user_decision
    ON evaluations(user_id, decision, evaluated_at DESC);

-- Trigger para updated_at
DROP TRIGGER IF EXISTS trg_evaluations_updated_at ON evaluations;
CREATE TRIGGER trg_evaluations_updated_at
    BEFORE UPDATE ON evaluations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- TRADERS: Visibles por todos, modificables por autenticados
ALTER TABLE traders ENABLE ROW LEVEL SECURITY;

-- Todos los usuarios autenticados pueden ver traders
DROP POLICY IF EXISTS "Traders are viewable by authenticated users" ON traders;
CREATE POLICY "Traders are viewable by authenticated users"
    ON traders FOR SELECT
    USING (auth.role() = 'authenticated');

-- Usuarios autenticados pueden crear traders
DROP POLICY IF EXISTS "Authenticated users can create traders" ON traders;
CREATE POLICY "Authenticated users can create traders"
    ON traders FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Usuarios autenticados pueden actualizar traders
DROP POLICY IF EXISTS "Authenticated users can update traders" ON traders;
CREATE POLICY "Authenticated users can update traders"
    ON traders FOR UPDATE
    USING (auth.role() = 'authenticated');

-- EVALUATIONS: Solo el propietario puede acceder
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own evaluations" ON evaluations;
CREATE POLICY "Users can view own evaluations"
    ON evaluations FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own evaluations" ON evaluations;
CREATE POLICY "Users can insert own evaluations"
    ON evaluations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own evaluations" ON evaluations;
CREATE POLICY "Users can update own evaluations"
    ON evaluations FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own evaluations" ON evaluations;
CREATE POLICY "Users can delete own evaluations"
    ON evaluations FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- VISTAS
-- ============================================

-- Vista: Resumen de evaluaciones con datos de trader
DROP VIEW IF EXISTS v_evaluations_summary;
CREATE VIEW v_evaluations_summary AS
SELECT
    e.id,
    e.created_at,
    e.evaluated_at,
    e.user_id,

    -- Datos del trader
    t.id AS trader_id,
    t.display_name AS trader_name,
    t.trading_style,
    t.binance_profile_url,
    t.tags AS trader_tags,

    -- Evaluación
    e.risk_profile,
    e.decision,
    e.total_score,

    -- Métricas extraídas
    (e.metrics->>'roi_30d_pct')::NUMERIC AS roi_30d,
    (e.metrics->>'roi_90d_pct')::NUMERIC AS roi_90d,
    (e.metrics->>'roi_180d_pct')::NUMERIC AS roi_180d,
    (e.metrics->>'max_drawdown_pct')::NUMERIC AS max_drawdown,
    (e.metrics->>'win_rate_pct')::NUMERIC AS win_rate,
    (e.metrics->>'avg_leverage')::NUMERIC AS avg_leverage,
    (e.metrics->>'copiers')::INTEGER AS copiers,

    -- Copy settings extraídos
    e.copy_settings->>'copy_mode' AS copy_mode,
    (e.copy_settings->>'order_size_usdt')::NUMERIC AS order_size_usdt,
    (e.copy_settings->>'daily_loss_cap_pct')::NUMERIC AS daily_loss_cap_pct,

    e.notes
FROM evaluations e
JOIN traders t ON t.id = e.trader_id;

-- Vista: Estadísticas por trader (últimas métricas de cualquier usuario)
DROP VIEW IF EXISTS v_trader_stats;
CREATE VIEW v_trader_stats AS
SELECT DISTINCT ON (t.id)
    t.id,
    t.display_name,
    t.trading_style,
    t.binance_profile_url,
    t.is_active,
    t.tags,

    -- Última evaluación
    e.evaluated_at AS last_evaluated,
    (e.metrics->>'roi_30d_pct')::NUMERIC AS latest_roi_30d,
    (e.metrics->>'roi_90d_pct')::NUMERIC AS latest_roi_90d,
    (e.metrics->>'max_drawdown_pct')::NUMERIC AS latest_max_drawdown,
    (e.metrics->>'win_rate_pct')::NUMERIC AS latest_win_rate,
    (e.metrics->>'copiers')::INTEGER AS latest_copiers,

    -- Conteo de evaluaciones
    (SELECT COUNT(*) FROM evaluations WHERE trader_id = t.id) AS total_evaluations
FROM traders t
LEFT JOIN evaluations e ON e.trader_id = t.id
ORDER BY t.id, e.evaluated_at DESC NULLS LAST;

-- ============================================
-- FUNCIONES AUXILIARES
-- ============================================

-- Función: Buscar o crear trader por nombre
CREATE OR REPLACE FUNCTION find_or_create_trader(
    p_display_name TEXT,
    p_binance_url TEXT DEFAULT NULL,
    p_style TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_trader_id UUID;
BEGIN
    -- Buscar trader existente por nombre o URL
    SELECT id INTO v_trader_id
    FROM traders
    WHERE display_name = p_display_name
       OR (p_binance_url IS NOT NULL AND binance_profile_url = p_binance_url)
    LIMIT 1;

    -- Si no existe, crear uno nuevo
    IF v_trader_id IS NULL THEN
        INSERT INTO traders (display_name, binance_profile_url, trading_style)
        VALUES (p_display_name, p_binance_url, p_style)
        RETURNING id INTO v_trader_id;
    END IF;

    RETURN v_trader_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función: Obtener criterios por perfil de riesgo
CREATE OR REPLACE FUNCTION get_default_criteria(p_risk_profile TEXT)
RETURNS JSONB AS $$
BEGIN
    RETURN CASE p_risk_profile
        WHEN 'conservative' THEN '{
            "roi_90d_range_pct": [10, 30],
            "max_drawdown_pct_lte": 10,
            "win_rate_pct_gte": 60,
            "min_days_active": 180,
            "leverage_range": [1, 2],
            "min_copiers": 100
        }'::JSONB
        WHEN 'moderate' THEN '{
            "roi_90d_range_pct": [20, 60],
            "max_drawdown_pct_lte": 20,
            "win_rate_pct_gte": 55,
            "min_days_active": 90,
            "leverage_range": [1, 3],
            "min_copiers": 50
        }'::JSONB
        WHEN 'aggressive' THEN '{
            "roi_90d_range_pct": [40, 200],
            "max_drawdown_pct_lte": 35,
            "win_rate_pct_gte": 50,
            "min_days_active": 60,
            "leverage_range": [1, 5],
            "min_copiers": 20
        }'::JSONB
        ELSE '{}'::JSONB
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- DATOS DE EJEMPLO (comentar en producción)
-- ============================================
/*
-- Insertar trader de ejemplo
INSERT INTO traders (display_name, binance_profile_url, trading_style, tags)
VALUES (
    'CryptoMaster123',
    'https://www.binance.com/es/copy-trading/lead-details?portfolioId=example123',
    'swing',
    ARRAY['top-performer', 'consistent']
);

-- Insertar evaluación de ejemplo (reemplazar user_id con uno válido)
INSERT INTO evaluations (
    user_id,
    trader_id,
    risk_profile,
    selection_criteria,
    metrics,
    copy_settings,
    decision,
    total_score,
    notes
)
VALUES (
    '00000000-0000-0000-0000-000000000000',  -- Reemplazar con user_id real
    (SELECT id FROM traders WHERE display_name = 'CryptoMaster123'),
    'moderate',
    get_default_criteria('moderate'),
    '{
        "roi_30d_pct": 38.5,
        "roi_90d_pct": 42.7,
        "roi_180d_pct": 51.2,
        "max_drawdown_pct": 14.5,
        "win_rate_pct": 61.0,
        "avg_leverage": 2.3,
        "copiers": 342,
        "days_active": 245
    }'::JSONB,
    '{
        "copy_mode": "fixed",
        "order_size_usdt": 50,
        "daily_loss_cap_pct": 3,
        "stop_copy_drawdown_pct": 12,
        "assets_whitelist": ["BTC", "ETH", "BNB", "SOL"]
    }'::JSONB,
    'approved',
    78.5,
    'Trader con estrategia swing consistente. Buen balance riesgo/retorno.'
);
*/

-- ============================================
-- FUNCIÓN: Calcular score de evaluación
-- ============================================
CREATE OR REPLACE FUNCTION calculate_evaluation_score(
    p_metrics JSONB,
    p_criteria JSONB
)
RETURNS NUMERIC AS $$
DECLARE
    v_score NUMERIC := 0;
    v_roi_90d NUMERIC;
    v_max_drawdown NUMERIC;
    v_win_rate NUMERIC;
    v_copiers INTEGER;
    v_days_active INTEGER;
BEGIN
    -- Extraer métricas
    v_roi_90d := COALESCE((p_metrics->>'roi_90d_pct')::NUMERIC, 0);
    v_max_drawdown := COALESCE((p_metrics->>'max_drawdown_pct')::NUMERIC, 100);
    v_win_rate := COALESCE((p_metrics->>'win_rate_pct')::NUMERIC, 0);
    v_copiers := COALESCE((p_metrics->>'copiers')::INTEGER, 0);
    v_days_active := COALESCE((p_metrics->>'days_active')::INTEGER, 0);

    -- ROI Score (30% peso, máx 30 puntos)
    -- Mayor ROI = mayor score, límite en 100% ROI
    v_score := v_score + LEAST(v_roi_90d, 100) * 0.30;

    -- Drawdown Score (25% peso, máx 25 puntos)
    -- Menor drawdown = mayor score
    v_score := v_score + GREATEST(25 - (v_max_drawdown * 0.5), 0);

    -- Win Rate Score (20% peso, máx 20 puntos)
    -- Mayor win rate = mayor score
    v_score := v_score + (v_win_rate * 0.20);

    -- Copiers Score (15% peso, máx 15 puntos)
    -- Más copiers = mayor score, escala logarítmica
    v_score := v_score + LEAST(LN(GREATEST(v_copiers, 1)) * 3, 15);

    -- Experience Score (10% peso, máx 10 puntos)
    -- Más días activo = mayor score, límite en 365 días
    v_score := v_score + LEAST(v_days_active / 36.5, 10);

    RETURN ROUND(LEAST(v_score, 100), 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- TRIGGER: Auto-calcular score en INSERT/UPDATE
-- ============================================
CREATE OR REPLACE FUNCTION auto_calculate_score()
RETURNS TRIGGER AS $$
BEGIN
    -- Si no se proporciona score, calcularlo automáticamente
    IF NEW.total_score IS NULL THEN
        NEW.total_score := calculate_evaluation_score(NEW.metrics, NEW.selection_criteria);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_evaluations_auto_score ON evaluations;
CREATE TRIGGER trg_evaluations_auto_score
    BEFORE INSERT OR UPDATE ON evaluations
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_score();

-- ============================================
-- VERIFICACIÓN
-- ============================================
-- SELECT * FROM traders;
-- SELECT * FROM evaluations;
-- SELECT * FROM v_evaluations_summary;
-- SELECT * FROM v_trader_stats;
-- SELECT get_default_criteria('moderate');
-- SELECT calculate_evaluation_score(
--     '{"roi_90d_pct": 45, "max_drawdown_pct": 15, "win_rate_pct": 60, "copiers": 500, "days_active": 180}'::jsonb,
--     '{}'::jsonb
-- );
