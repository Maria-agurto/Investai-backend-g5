# ═══════════════════════════════════════════════════════════════
# InvestAI — Backend API (Entregable 5)
# Sirve datos de mercado REALES (OHLCV) usando yfinance.
# Sustituye la simulación Math.sin/seed() del frontend Módulo 6.2.
#
# Endpoints:
#   GET /api/market/<ticker>?interval=1D|1W|1M|3M|1A
#       -> velas OHLCV históricas para el gráfico de velas + volumen
#   GET /api/quotes
#       -> precio actual y variación % de todos los tickers del watchlist
#
# Ejecutar:
#   pip install -r requirements.txt
#   python app.py
#   (sirve en http://127.0.0.1:5000)
# ═══════════════════════════════════════════════════════════════

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)  # Permite que el frontend (abierto como archivo HTML o en otro puerto) llame a esta API

# ── Configuración de activos (igual que en el frontend) ──
TICKERS_INFO = {
    "AAPL":    {"name": "Apple Inc.",      "cap": "2.94T"},
    "MSFT":    {"name": "Microsoft Corp.", "cap": "3.07T"},
    "GOOGL":   {"name": "Alphabet Inc.",   "cap": "2.18T"},
    "NVDA":    {"name": "NVIDIA Corp.",    "cap": "2.14T"},
    "BTC-USD": {"name": "Bitcoin",         "cap": "1.32T"},
}

# El frontend usa "BTC" como id corto; yfinance necesita "BTC-USD"
def resolver_simbolo(ticker: str) -> str:
    ticker = ticker.upper()
    return "BTC-USD" if ticker == "BTC" else ticker

# Cuántos días de histórico pedir según el intervalo elegido en el frontend
# (se añade un colchón extra para poder calcular SMA50 / Bollinger en el cliente)
INTERVAL_DAYS = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "1A": 252}
BUFFER_DIAS = 70  # días extra para que SMA50 tenga suficiente historia desde el primer punto visible


@app.route("/api/market/<ticker>")
def get_market_data(ticker):
    """
    Devuelve velas OHLCV reales para un ticker.
    Reemplaza a la función genOHLC() (pseudo-random) del frontend original.
    """
    interval = request.args.get("interval", "1M")
    dias_visibles = INTERVAL_DAYS.get(interval, 30)
    simbolo = resolver_simbolo(ticker)

    try:
        periodo_dias = dias_visibles + BUFFER_DIAS
        df = yf.download(
            simbolo,
            period=f"{periodo_dias}d",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )

        if df is None or df.empty:
            return jsonify({"error": f"No se encontraron datos para {ticker}"}), 404

        # yfinance puede devolver columnas MultiIndex cuando se pasa un solo ticker en versiones recientes
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        respuesta = {
            "ticker": ticker.upper(),
            "symbol_yfinance": simbolo,
            "name": TICKERS_INFO.get(simbolo, {}).get("name", ticker),
            "cap": TICKERS_INFO.get(simbolo, {}).get("cap", "N/A"),
            "dates":  df.index.strftime("%Y-%m-%d").tolist(),
            "opens":  df["Open"].round(2).tolist(),
            "highs":  df["High"].round(2).tolist(),
            "lows":   df["Low"].round(2).tolist(),
            "closes": df["Close"].round(2).tolist(),
            "vols":   df["Volume"].astype(int).tolist(),
            "fuente": "Yahoo Finance (yfinance)",
        }
        return jsonify(respuesta)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quotes")
def get_quotes():
    """
    Devuelve precio actual + variación % de todos los tickers del watchlist.
    Usado para poblar la barra lateral con precios reales.
    """
    simbolos = list(TICKERS_INFO.keys())
    try:
        data = yf.download(simbolos, period="5d", interval="1d", progress=False, auto_adjust=True)

        resultado = {}
        closes = data["Close"]
        for simbolo in simbolos:
            serie = closes[simbolo].dropna()
            if len(serie) < 2:
                continue
            ultimo = float(serie.iloc[-1])
            anterior = float(serie.iloc[-2])
            cambio_pct = (ultimo - anterior) / anterior * 100
            ticker_corto = "BTC" if simbolo == "BTC-USD" else simbolo
            resultado[ticker_corto] = {
                "price": round(ultimo, 2),
                "change_pct": round(cambio_pct, 2),
            }
        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "InvestAI Market Data API"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
