from datetime import date, datetime, timedelta
from typing import List, Optional, Dict

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Date, ForeignKey, select, func, event
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
DB_URL = "sqlite:///./stocks.db"
TOP10 = [
    # Top 10 (NSE) – API uses these symbols; backend maps them to yfinance tickers
    {"name": "Reliance Industries Ltd",        "symbol": "RELIANCE"},
    {"name": "Tata Consultancy Services",      "symbol": "TCS"},
    {"name": "Infosys Ltd",                    "symbol": "INFY"},
    {"name": "HDFC Bank Ltd",                  "symbol": "HDFCBANK"},
    {"name": "ICICI Bank Ltd",                 "symbol": "ICICIBANK"},
    {"name": "State Bank of India",            "symbol": "SBIN"},
    {"name": "Bajaj Finance Ltd",              "symbol": "BAJFINANCE"},
    {"name": "Larsen & Toubro Ltd",            "symbol": "LT"},
    {"name": "ITC Ltd",                        "symbol": "ITC"},
    {"name": "Bharti Airtel Ltd",              "symbol": "BHARTIARTL"},
]
# Map your app symbols -> yfinance tickers
YF_MAP = {
    "RELIANCE":   "RELIANCE.NS",
    "TCS":        "TCS.NS",
    "INFY":       "INFY.NS",
    "HDFCBANK":   "HDFCBANK.NS",
    "ICICIBANK":  "ICICIBANK.NS",
    "SBIN":       "SBIN.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "LT":         "LT.NS",
    "ITC":        "ITC.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    # if you later add US symbols, they map to themselves (e.g., "AAPL": "AAPL")
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
Base = declarative_base()
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Company(Base):
    __tablename__ = "companies"
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    prices = relationship("Price", back_populates="company", cascade="all, delete-orphan")

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, ForeignKey("companies.symbol"), index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    company = relationship("Company", back_populates="prices")

Base.metadata.create_all(engine)

# Seed companies if table is empty
def seed_companies():
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Company))
        if count == 0:
            for c in TOP10:
                db.add(Company(symbol=c["symbol"], name=c["name"]))
            db.commit()

seed_companies()

# -----------------------------------------------------------------------------
# Schemas (Pydantic)
# -----------------------------------------------------------------------------
class CompanyOut(BaseModel):
    symbol: str
    name: str

class PriceOut(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockSeriesOut(BaseModel):
    symbol: str
    name: str
    count: int
    data: List[PriceOut]

# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
app = FastAPI(title="Stock Dashboard Backend", version="1.0.0")

# CORS for local React dev and others; adjust origins for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev: you can restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def yf_symbol(symbol: str) -> Optional[str]:
    """Map app symbol to yahoo ticker; return None if unknown."""
    return YF_MAP.get(symbol, None)

def fetch_and_store(symbol: str, days: int = 30):
    """
    Ensure we have at least `days` of data for `symbol` in DB.
    Fetch from yfinance (last ~45 days daily) and upsert rows.
    """
    yfs = yf_symbol(symbol)
    if not yfs:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not supported")

    # Download ~45 days to be safe for market holidays
    df = yf.download(
        yfs,
        period="2mo",          # ~60 days; safer for holidays/weekends
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=True,
    )

    if df is None or df.empty:
        raise HTTPException(status_code=502, detail=f"Failed to fetch data for {symbol}")

    # Normalize df
    df = df.reset_index()  # Date becomes a column
    # yfinance sometimes uses tz-aware timestamps; convert to date
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Upsert into SQLite
    with SessionLocal() as db:
        # Ensure company exists
        comp = db.get(Company, symbol)
        if not comp:
            raise HTTPException(status_code=404, detail=f"Company '{symbol}' not found in DB")

        # Insert or update per day
        for _, row in df.iterrows():
            d = row["Date"]
            existing = db.query(Price).filter(Price.symbol == symbol, Price.date == d).first()
            if existing:
                existing.open = float(row["Open"]) if pd.notna(row["Open"]) else None
                existing.high = float(row["High"]) if pd.notna(row["High"]) else None
                existing.low = float(row["Low"]) if pd.notna(row["Low"]) else None
                existing.close = float(row["Close"]) if pd.notna(row["Close"]) else None
                existing.volume = int(row["Volume"]) if pd.notna(row["Volume"]) else None
            else:
                db.add(
                    Price(
                        symbol=symbol,
                        date=d,
                        open=float(row["Open"]) if pd.notna(row["Open"]) else None,
                        high=float(row["High"]) if pd.notna(row["High"]) else None,
                        low=float(row["Low"]) if pd.notna(row["Low"]) else None,
                        close=float(row["Close"]) if pd.notna(row["Close"]) else None,
                        volume=int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                    )
                )
        db.commit()

def get_last_n_days_from_db(symbol: str, days: int) -> List[Price]:
    cutoff = date.today() - timedelta(days=days + 5)  # cushion for weekends/holidays
    with SessionLocal() as db:
        q = (
            db.query(Price)
            .filter(Price.symbol == symbol, Price.date >= cutoff)
            .order_by(Price.date.asc())
        )
        return q.all()

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/companies", response_model=List[CompanyOut])
def list_companies():
    with SessionLocal() as db:
        rows = db.execute(select(Company).order_by(Company.name.asc())).scalars().all()
        return [{"symbol": r.symbol, "name": r.name} for r in rows]

@app.get("/stocks/{symbol}", response_model=StockSeriesOut)
def get_stock_series(symbol: str, days: int = 30, refresh: bool = True):
    """
    Returns last `days` daily OHLCV bars for `symbol`.
    - `refresh=true` (default) fetches from Yahoo and upserts into DB before reading.
    - Set `refresh=false` to read only from DB.
    """
    # Ensure symbol exists in DB
    with SessionLocal() as db:
        comp = db.get(Company, symbol)
        if not comp:
            raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'")

    if refresh:
        fetch_and_store(symbol, days=days)

    rows = get_last_n_days_from_db(symbol, days)
    if not rows:
        # If DB empty and refresh was false, try once
        fetch_and_store(symbol, days=days)
        rows = get_last_n_days_from_db(symbol, days)

    data = [
        PriceOut(
            date=r.date,
            open=r.open or 0.0,
            high=r.high or 0.0,
            low=r.low or 0.0,
            close=r.close or 0.0,
            volume=r.volume or 0,
        )
        for r in rows
    ]
    return {
        "symbol": symbol,
        "name": next((c["name"] for c in TOP10 if c["symbol"] == symbol), symbol),
        "count": len(data),
        "data": data[-days:],  # trim to exactly N if we overshot
    }

@app.get("/")
def health():
    return {"status": "ok", "message": "Stock Dashboard Backend running"}
