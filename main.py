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

# Eski kodundaki akıllı BIST listesi
BIST = {"THYAO","GARAN","AKBNK","YKBNK","ISCTR","HALKB","VAKBN","SISE","EREGL","KRDMD",
        "BIMAS","MGROS","ARCLK","TOASO","FROTO","DOAS","OTKAR","KCHOL","SAHOL","PETKM",
        "TUPRS","AYGAZ","AKSA","VESBE","VESTL","TCELL","TTKOM","ASELS","KOZAL","KOZAA",
        "ENKAI","EKGYO","ISGYO","TSKB","ALARK","ALGYO","SODA","TRKCM","NETAS","LOGO",
        "INDES","DOHOL","TKFEN","TATGD","ULKER","PGSUS","TAVHL","CLEBI","MAVI","BERA",
        "BRISA","GUBRF","HEKTS","KARSAN","SASA","SOKM","QNBFL","QNBFB","SARKY","SKTAS"}

def resolve_ticker(raw_ticker: str):
    t = raw_ticker.upper().strip()
    if any(c in t for c in [".","-","="]): return t
    return t + ".IS" if t in BIST else t

@app.get("/")
def read_root():
    return {"status": "API is online", "platform": "ARD Finans Mobile & Web"}

@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    try:
        resolved_ticker = resolve_ticker(ticker)
        df = yf.download(resolved_ticker, period="1mo", interval="1d", progress=False)
        
        if df.empty:
            return {"error": f"Veri bulunamadı. Aranan sembol: {resolved_ticker}"}
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df.reset_index(inplace=True)
        date_col = "Date" if "Date" in df.columns else "Datetime"
        if date_col in df.columns:
            df[date_col] = df[date_col].astype(str)
            
        df = df.where(pd.notnull(df), None)
        
        return {"ticker": resolved_ticker, "data": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": f"API Hatası: {str(e)}"}
