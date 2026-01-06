"""
Mock Leaderboard Data

Datos de prueba realistas del Binance Leaderboard para desarrollo y testing.

Nota: Estos datos son ficticios pero siguen la estructura real del API de Binance.
"""

import random
from datetime import datetime, timedelta


def generate_mock_leaderboard(period: str = "WEEKLY", limit: int = 100) -> dict:
    """
    Genera datos de leaderboard simulados.

    Args:
        period: DAILY, WEEKLY, MONTHLY, ALL
        limit: Número de traders a generar

    Returns:
        Dict con estructura del API de Binance
    """

    # Nombres de traders ficticios
    trader_names = [
        "CryptoMaster", "MoonTrader", "BTCWhale", "ETHKing", "FuturesGuru",
        "DiamondHands", "ProfitSeeker", "ChartWizard", "TrendFollower", "SwingMaster",
        "RiskTaker", "SafeTrader", "HighLeverager", "Conservative1", "Aggressive99",
        "SmartInvestor", "QuickScalper", "LongTermBull", "ShortKing", "HedgeMaster",
        "AlgoTrader", "PatternPro", "BreakoutHunter", "SupportResist", "FibonacciMan",
        "EMACrosser", "RSIExpert", "MACDMaster", "BollingerKing", "StochRSI",
        "VolumeTrader", "OrderFlowPro", "LiquiditySeeker", "MarketMaker99", "ArbitrageKing",
        "TrendRider", "RangeBound", "MomentumMan", "MeanReversion", "StatArb",
        "GridTrader", "ScalpingBot", "PositionTrader", "IntraDay", "Overnight",
        "MarginCall", "StopLoss", "TakeProfit", "HodlForever", "DayTrader"
    ]

    # Generar traders con métricas realistas según perfil
    traders = []

    for i in range(limit):
        # Decidir perfil del trader
        profile_choice = random.choices(
            ["conservative", "moderate", "aggressive"],
            weights=[0.2, 0.5, 0.3]
        )[0]

        # Generar métricas según perfil
        if profile_choice == "conservative":
            roi = round(random.uniform(10, 30), 2)
            pnl = round(random.uniform(500, 5000), 2)
            win_rate = round(random.uniform(60, 75), 1)
            leverage = round(random.uniform(1, 2), 1)
        elif profile_choice == "moderate":
            roi = round(random.uniform(20, 60), 2)
            pnl = round(random.uniform(1000, 15000), 2)
            win_rate = round(random.uniform(55, 70), 1)
            leverage = round(random.uniform(1.5, 3), 1)
        else:  # aggressive
            roi = round(random.uniform(40, 150), 2)
            pnl = round(random.uniform(2000, 50000), 2)
            win_rate = round(random.uniform(50, 65), 1)
            leverage = round(random.uniform(2.5, 5), 1)

        # Número de seguidores correlacionado con ROI
        base_followers = int(50 + (roi * 5))
        follower_count = base_followers + random.randint(-30, 100)

        # Generar UID encriptado falso
        encrypted_uid = f"{''.join(random.choices('ABCDEF0123456789', k=32))}"

        # Nombre único
        name_suffix = f"{i+1:02d}" if i < len(trader_names) else f"{random.randint(100,999)}"
        nick_name = f"{random.choice(trader_names)}{name_suffix}"

        trader = {
            "nickName": nick_name,
            "encryptedUid": encrypted_uid,
            "roi": roi,
            "pnl": pnl,
            "rank": i + 1,
            "followerCount": max(1, follower_count),
            "winRate": win_rate,
            "avgLeverage": leverage,
            "positionShared": random.choice([True, False]),
            "twitterUrl": f"https://twitter.com/{nick_name.lower()}" if random.random() > 0.7 else None
        }

        traders.append(trader)

    # Ordenar por ROI descendente
    traders.sort(key=lambda x: x["roi"], reverse=True)

    # Actualizar ranks
    for i, trader in enumerate(traders, 1):
        trader["rank"] = i

    # Estructura de respuesta del API
    response = {
        "code": "000000",
        "message": None,
        "messageDetail": None,
        "data": traders,
        "success": True
    }

    return response


def generate_mock_trader_details(encrypted_uid: str) -> dict:
    """
    Genera detalles mockeados de un trader específico.

    Args:
        encrypted_uid: UID del trader

    Returns:
        Dict con detalles del trader
    """

    # Datos históricos de rendimiento
    daily_data = []
    cumulative_pnl = 0

    for day in range(30):
        daily_pnl = round(random.uniform(-500, 1000), 2)
        cumulative_pnl += daily_pnl

        daily_data.append({
            "date": (datetime.now() - timedelta(days=30-day)).strftime("%Y-%m-%d"),
            "pnl": daily_pnl,
            "cumulativePnl": round(cumulative_pnl, 2),
            "roi": round((cumulative_pnl / 10000) * 100, 2)
        })

    response = {
        "code": "000000",
        "message": None,
        "data": {
            "encryptedUid": encrypted_uid,
            "nickName": f"MockTrader_{encrypted_uid[:8]}",
            "roi30d": round(random.uniform(10, 50), 2),
            "roi90d": round(random.uniform(20, 80), 2),
            "maxDrawdown": round(random.uniform(5, 25), 2),
            "sharpeRatio": round(random.uniform(1, 3), 2),
            "followerCount": random.randint(50, 500),
            "dailyData": daily_data,
            "topPositions": [
                {"symbol": "BTCUSDT", "percentage": 40},
                {"symbol": "ETHUSDT", "percentage": 30},
                {"symbol": "BNBUSDT", "percentage": 20},
                {"symbol": "SOLUSDT", "percentage": 10}
            ]
        },
        "success": True
    }

    return response


# Para testing
if __name__ == "__main__":
    import json

    # Generar leaderboard de prueba
    data = generate_mock_leaderboard("WEEKLY", 20)

    print("=== MOCK LEADERBOARD DATA ===\n")
    print(f"Total traders: {len(data['data'])}")
    print(f"\nTop 5 traders:")

    for trader in data['data'][:5]:
        print(f"  {trader['rank']}. {trader['nickName']}")
        print(f"     ROI: {trader['roi']}% | PnL: ${trader['pnl']} | Followers: {trader['followerCount']}")

    print(f"\n Sample JSON structure:")
    print(json.dumps(data['data'][0], indent=2))
