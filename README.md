# Investai-backend-g5
# Entregable 5 — Frontend Conectado al Backend
**InvestAI · iDeSo · UNMSM · FISI**

## Qué se hizo

Se tomó el frontend de la Semana 10 **`modulo6_2_mercado.html`** (Datos de Mercado) y se creó
**`modulo6_2_mercado_conectado.html`**, donde la generación de velas OHLC con una función
pseudo-aleatoria (`seed()` basada en `Math.sin`, equivalente a `Math.random()`) fue **reemplazada
por `fetch()` real al backend**.

Esto demuestra el ciclo completo: **Frontend → fetch() → Backend Flask → yfinance → JSON → Gráfico**.

| Antes | Después |
|---|---|
| `genOHLC(ticker, nDays)` generaba velas con `Math.sin()` como semilla pseudo-aleatoria | `fetchOHLC(ticker, interval)` hace `fetch()` a `GET /api/market/<ticker>` y trae datos OHLCV **reales** vía `yfinance` |
| Precios del watchlist hardcodeados en el HTML | `fetchQuotes()` hace `fetch()` a `GET /api/quotes` y trae precio + variación % reales |
| Sin manejo de errores de red | Indicador de conexión (punto verde/ámbar/rojo) + banner si el backend no responde |

Los cálculos de **SMA20, SMA50 y Bandas de Bollinger** se mantienen en el cliente (JavaScript),
ya que son lógica de presentación que no requiere ir y volver al servidor — el backend solo
entrega los datos crudos (OHLCV), separando responsabilidades como en una arquitectura real.

## Estructura de archivos

```
entregable5/
├── modulo6_2_mercado_conectado.html   ← Frontend modificado (Entregable 5)
├── backend/
│   ├── app.py                          ← API Flask
│   └── requirements.txt
└── README_ENTREGABLE5.md
```

## Cómo ejecutarlo

### 1. Levantar el backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Esto inicia el servidor en `http://127.0.0.1:5000`. Verifica que está vivo en:
`http://127.0.0.1:5000/api/health`

### 2. Abrir el frontend

Abre `modulo6_2_mercado_conectado.html` directamente en el navegador (doble clic, o
`Live Server` en VSCode). El punto de estado en la barra superior pasará de
**"CONECTANDO AL BACKEND…"** a **"MERCADO EN VIVO · API CONECTADA"** (verde) si todo
funciona, o mostrará un banner rojo si el backend no está corriendo.

> Si en algún momento cambias el puerto o despliegas el backend en otra URL, solo edita
> la constante `API_BASE_URL` al inicio del `<script>` del HTML.

## Endpoints del backend

| Endpoint | Descripción |
|---|---|
| `GET /api/market/<ticker>?interval=1D\|1W\|1M\|3M\|1A` | Velas OHLCV reales (fechas, open, high, low, close, volumen) para el ticker e intervalo pedidos |
| `GET /api/quotes` | Precio actual y variación % de todos los tickers del watchlist (AAPL, MSFT, GOOGL, NVDA, BTC-USD) |
| `GET /api/health` | Chequeo de salud del servicio |

Ejemplo de respuesta de `/api/market/AAPL?interval=1M`:
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "cap": "2.94T",
  "dates": ["2026-04-01", "2026-04-02", "..."],
  "opens": [170.20, 171.05, "..."],
  "highs": [172.10, 172.80, "..."],
  "lows": [169.40, 170.30, "..."],
  "closes": [171.50, 172.10, "..."],
  "vols": [48230000, 51120000, "..."],
  "fuente": "Yahoo Finance (yfinance)"
}
```

## Notas

- El backend usa `yfinance` (la misma librería que el Notebook 2 — Clasificador SVC), así que
  los precios mostrados son datos bursátiles reales, no simulados.
- Si `yfinance` no logra conectarse a Yahoo Finance (sin internet, ticker inválido, etc.), el
  backend responde con un JSON de error y código HTTP apropiado (404/500); el frontend lo
  captura y muestra el banner de "Backend desconectado" en vez de inventar datos.
- Este mismo patrón (endpoint Flask + `fetch()` + JSON) es el que se podría reusar para
  conectar `datos_svc.json` (Notebook 2), los clasificadores RNN (Notebook 3) o el regresor
  LSTM de pronóstico de precios (Notebook 4) a sus respectivos módulos del frontend.
