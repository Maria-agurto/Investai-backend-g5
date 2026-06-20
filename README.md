# Investai-backend-g5
# Entregable 5 — Frontend Conectado al Backend
**InvestAI · iDeSo · UNMSM · FISI**

## Qué se hizo

Se tomó el frontend de la Semana 10 **`modulo6_2_mercado.html`** (Datos de Mercado) y se creó
**`modulo6_2_mercado_ENTREGABLE5.html`**, donde la generación de velas OHLC con una función
pseudo-aleatoria (`seed()` basada en `Math.sin`, equivalente a `Math.random()`) fue **reemplazada
por `fetch()` real al backend**.

Esto demuestra el ciclo completo: **Frontend → fetch() → Backend FastAPI (Colab + ngrok) → yfinance → JSON → Gráfico**.

| Antes | Después |
|---|---|
| `genOHLC(ticker, nDays)` generaba velas con `Math.sin()` como semilla pseudo-aleatoria | `fetchLSTM(ticker, horizonte)` hace `fetch()` a `GET /api/lstm/{ticker}` y trae datos **reales** del backend |
| Precios del watchlist hardcodeados en el HTML | Los valores de precio y métricas se actualizan desde la respuesta JSON del backend |
| Sin manejo de errores de red | Panel de diagnóstico + indicador de conexión (verde/rojo) + detección de errores CORS, timeout y HTTP |

Los cálculos de **SMA, Bollinger y error %** se mantienen en el cliente (JavaScript),
ya que son lógica de presentación — el backend entrega los datos crudos, separando
responsabilidades como en una arquitectura real.

## Estructura de archivos

```
entregable5/
├── modulo6_2_mercado_ENTREGABLE5.html   ← Frontend modificado (Entregable 5)
├── API_REST_con_FastAPI.ipynb            ← Backend FastAPI (Google Colab)
└── README.md
```

> El backend vive en el Notebook `API_REST_con_FastAPI.ipynb` ejecutado en Google Colab,
> expuesto públicamente mediante **ngrok**. No se requiere `app.py` ni `requirements.txt`
> separados: la Celda 1 del Notebook instala las dependencias y la Celda 3 lanza el servidor.

## Cómo ejecutarlo

### 1. Levantar el backend (Google Colab)

1. Abre `API_REST_con_FastAPI.ipynb` en Google Colab.
2. Ejecuta las **3 celdas en orden**.
3. La Celda 3 imprimirá la URL pública de ngrok, por ejemplo:
   ```
   https://frugality-protract-sublime.ngrok-free.dev
   ```
4. Verifica que el backend está vivo abriendo en el navegador:
   `https://<tu-url-ngrok>/api/salud`  
   Deberías ver: `{"status": "healthy", ...}`

> **Nota:** La URL de ngrok cambia cada vez que se reinicia la sesión de Colab (sesiones
> gratuitas duran ~2 horas). Cuando esto ocurra, vuelve a ejecutar la Celda 3 y copia
> la nueva URL.

### 2. Conectar el frontend

1. Abre `modulo6_2_mercado_ENTREGABLE5.html` en el navegador.
2. Pega la URL de ngrok en el campo **Backend API** (barra azul oscura superior).
3. Pulsa **Conectar** — el indicador pasará a verde: **"API EN VIVO"**.
4. Haz clic en cualquier ticker del watchlist para cargar datos reales del backend.

> Si el navegador bloquea la conexión (página de advertencia de ngrok), usa el botón
> **🔗 Probar URL** para abrir `/api/salud` en una pestaña nueva, acepta la advertencia
> y vuelve a pulsar Conectar.

## Endpoints del backend

| Endpoint | Descripción |
|---|---|
| `GET /api/salud` | Chequeo de salud del servicio |
| `GET /api/lstm/{ticker}?horizonte={n}` | Histórico real vs. predicho + proyección futura a `n` días con bandas de confianza al 95% |
| `GET /api/rnns/{ticker}` | Señales de clasificación de 4 arquitecturas RNN (LSTM, BiLSTM, GRU, SimpleRNN) |

Ejemplo de respuesta de `/api/lstm/FSM?horizonte=30`:
```json
{
  "ticker": "FSM",
  "metricas_error": {
    "rmse_usd": 0.3542,
    "rmse_porcentaje": 4.0,
    "mae_usd": 0.2834,
    "r2_score": 0.885
  },
  "historico_validacion": [
    { "fecha": "2026-05-01", "real": 8.91, "predicho": 8.87 },
    "..."
  ],
  "proyeccion_futura": [
    { "fecha": "2026-06-21", "prediccion_usd": 9.05, "banda_min": 8.35, "banda_max": 9.75 },
    "..."
  ]
}
```

## Notas

- El backend usa `yfinance` (la misma librería que el Notebook 2 — Clasificador SVC), así que
  los precios mostrados son datos bursátiles reales, no simulados.
- Las señales **BUY / SELL / HOLD** del clasificador SVC (`datos_svc.json`, Notebook 2)
  se muestran en el sidebar del frontend sin llamada adicional al backend, cargadas
  directamente desde el JSON generado por el modelo.
- Si el backend no responde (Colab desconectado, URL expirada, ticker inválido), el frontend
  captura el error y muestra un panel de diagnóstico con la causa exacta y los pasos
  para resolverlo, en vez de inventar datos.
- Este mismo patrón (`fetch()` → endpoint FastAPI → JSON) es extensible para conectar
  los clasificadores RNN (Notebook 3) o cualquier otro módulo del frontend al backend.
