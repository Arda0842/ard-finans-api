from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI(title="ARD Finans API")

# Mobil uygulamadan ve webden gelecek isteklere izin vermek için CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API is online", "platform": "ARD Finans Mobile & Web"}

@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    try:
        df = yf.download(ticker, period="1mo", interval="1d")
        df.reset_index(inplace=True)
        df['Date'] = df['Date'].astype(str)
        return {"ticker": ticker, "data": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}
