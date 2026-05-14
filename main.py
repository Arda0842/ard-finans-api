from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI(title="ARD Finans API")

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
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        if df.empty:
            return {"error": "Veri bulunamadı"}
            
        # 1. MultiIndex Sütun Düzeltmesi (yfinance'in yeni sürümleri için)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 2. Tarih formatını düzeltme
        df.reset_index(inplace=True)
        date_col = "Date" if "Date" in df.columns else "Datetime"
        if date_col in df.columns:
            df[date_col] = df[date_col].astype(str)
            
        # 3. NaN (boş) değerleri JSON'a uygun Null (None) değerlerine çevirme
        df = df.where(pd.notnull(df), None)
        
        return {"ticker": ticker, "data": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": f"API Hatası: {str(e)}"}
