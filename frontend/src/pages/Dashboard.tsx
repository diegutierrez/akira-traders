import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllTraders, getAllEvaluations, type EvaluationSummary } from '../services/evaluations';
import { useAuth } from '../contexts/AuthContext';

interface Stats {
  totalTraders: number;
  totalEvaluations: number;
  approvedTraders: number;
  avgRoi30d: number;
}

export function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({
    totalTraders: 0,
    totalEvaluations: 0,
    approvedTraders: 0,
    avgRoi30d: 0,
  });
  const [recentEvaluations, setRecentEvaluations] = useState<EvaluationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [traders, evaluations] = await Promise.all([getAllTraders(), getAllEvaluations()]);

        const approved = evaluations.filter((e) => e.decision === 'approved');
        const avgRoi =
          evaluations.length > 0
            ? evaluations.reduce((sum, e) => sum + (e.roi_30d || 0), 0) / evaluations.length
            : 0;

        setStats({
          totalTraders: traders.length,
          totalEvaluations: evaluations.length,
          approvedTraders: approved.length,
          avgRoi30d: avgRoi,
        });

        setRecentEvaluations(evaluations.slice(0, 5));
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const StatCard = ({
    title,
    value,
    subtitle,
    icon,
    color,
  }: {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    color: string;
  }) => (
    <div className="bg-bg-secondary rounded-lg p-6 border border-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-text-secondary text-sm">{title}</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{value}</p>
          {subtitle && <p className="text-text-tertiary text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>{icon}</div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="py-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-text-secondary mt-1">
          Bienvenido, {user?.user_metadata?.full_name || user?.email}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Traders"
          value={stats.totalTraders}
          icon={
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          }
          color="bg-blue-500"
        />
        <StatCard
          title="Evaluaciones"
          value={stats.totalEvaluations}
          icon={
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          }
          color="bg-purple-500"
        />
        <StatCard
          title="Aprobados"
          value={stats.approvedTraders}
          subtitle={
            stats.totalEvaluations > 0
              ? `${((stats.approvedTraders / stats.totalEvaluations) * 100).toFixed(0)}% del total`
              : undefined
          }
          icon={
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
          color="bg-green-500"
        />
        <StatCard
          title="ROI Promedio 30d"
          value={`${stats.avgRoi30d.toFixed(2)}%`}
          icon={
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
          }
          color="bg-yellow-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-bg-secondary rounded-lg p-6 border border-border">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Acciones Rápidas</h2>
          <div className="space-y-3">
            <Link
              to="/traders"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-bg-tertiary transition-colors"
            >
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg
                  className="h-5 w-5 text-blue-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </div>
              <div>
                <p className="text-text-primary font-medium">Sincronizar Traders</p>
                <p className="text-text-tertiary text-sm">
                  Importar traders de Binance Copy Trading
                </p>
              </div>
            </Link>
            <Link
              to="/evaluations/new"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-bg-tertiary transition-colors"
            >
              <div className="p-2 bg-green-500/20 rounded-lg">
                <svg
                  className="h-5 w-5 text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
              <div>
                <p className="text-text-primary font-medium">Nueva Evaluación</p>
                <p className="text-text-tertiary text-sm">
                  Evaluar un trader con criterios personalizados
                </p>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Evaluations */}
        <div className="bg-bg-secondary rounded-lg p-6 border border-border">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Evaluaciones Recientes</h2>
          {recentEvaluations.length === 0 ? (
            <p className="text-text-tertiary text-sm">No hay evaluaciones aún</p>
          ) : (
            <div className="space-y-3">
              {recentEvaluations.map((evaluation) => (
                <div
                  key={evaluation.id}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-tertiary transition-colors"
                >
                  <div>
                    <p className="text-text-primary font-medium">{evaluation.trader_name}</p>
                    <p className="text-text-tertiary text-xs">
                      {new Date(evaluation.evaluated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      evaluation.decision === 'approved'
                        ? 'bg-green-500/20 text-green-400'
                        : evaluation.decision === 'rejected'
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                    }`}
                  >
                    {evaluation.decision || 'pendiente'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
