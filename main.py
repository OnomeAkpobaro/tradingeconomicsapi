"""
Trading Economics FastAPI Application

This application provides endpoints to retrieve economic indicators
(interest rates, GDP growth, inflation, unemployment) for various countries
using the Trading Economics Python package.

Installation requirements:
pip install fastapi uvicorn tradingeconomics pandas python-dotenv

Usage:
1. Set your Trading Economics API key as environment variable:
   export TRADING_ECONOMICS_API_KEY='your_api_key_here'
   
2. Run the application:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

3. Access the API documentation at: http://localhost:8000/docs
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tradingeconomics as te
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trading Economics API",
    description="Access economic indicators for countries worldwide",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Trading Economics client
API_KEY = os.getenv('TRADING_ECONOMICS_API_KEY', 'guest:guest')
te.login(API_KEY)

# Response models
class EconomicIndicator(BaseModel):
    country: str
    indicator: str
    value: Optional[float]
    previous_value: Optional[float]
    last_update: Optional[str]
    unit: Optional[str]
    frequency: Optional[str]

class CountryEconomicData(BaseModel):
    country: str
    interest_rate: Optional[EconomicIndicator]
    gdp_growth: Optional[EconomicIndicator]
    inflation_rate: Optional[EconomicIndicator]
    unemployment_rate: Optional[EconomicIndicator]
    last_updated: str

class CurrencyPairData(BaseModel):
    base_currency: str
    quote_currency: str
    base_country_data: CountryEconomicData
    quote_country_data: CountryEconomicData

# Helper functions
def safe_get_indicator_data(country: str, indicator: str) -> Optional[Dict]:
    """Safely retrieve indicator data with error handling"""
    try:
        data = te.getIndicatorData(country=country, indicators=indicator, output_type='df')
        if data is not None and not data.empty:
            latest = data.iloc[-1]
            return {
                'country': latest.get('Country', country),
                'indicator': indicator,
                'value': latest.get('LastUpdate', None),
                'previous_value': latest.get('PreviousValue', None),
                'last_update': latest.get('LastUpdate', None),
                'unit': latest.get('Unit', None),
                'frequency': latest.get('Frequency', None)
            }
    except Exception as e:
        logger.warning(f"Error fetching {indicator} for {country}: {str(e)}")
    return None

def get_country_economic_data(country: str) -> CountryEconomicData:
    """Get all economic indicators for a country"""
    indicators = {
        'interest_rate': 'Interest Rate',
        'gdp_growth': 'GDP Growth Rate',
        'inflation_rate': 'Inflation Rate',
        'unemployment_rate': 'Unemployment Rate'
    }
    
    data = {}
    for key, indicator in indicators.items():
        indicator_data = safe_get_indicator_data(country, indicator)
        if indicator_data:
            data[key] = EconomicIndicator(**indicator_data)
        else:
            data[key] = None
    
    return CountryEconomicData(
        country=country,
        **data,
        last_updated=datetime.now().isoformat()
    )

# Currency to country mapping (major currencies)
CURRENCY_COUNTRY_MAP = {
    'USD': 'United States',
    'EUR': 'Euro Area',
    'GBP': 'United Kingdom',
    'JPY': 'Japan',
    'CHF': 'Switzerland',
    'CAD': 'Canada',
    'AUD': 'Australia',
    'NZD': 'New Zealand',
    'SEK': 'Sweden',
    'NOK': 'Norway',
    'DKK': 'Denmark',
    'PLN': 'Poland',
    'CZK': 'Czech Republic',
    'HUF': 'Hungary',
    'SGD': 'Singapore',
    'HKD': 'Hong Kong',
    'KRW': 'South Korea',
    'CNY': 'China',
    'INR': 'India',
    'BRL': 'Brazil',
    'MXN': 'Mexico',
    'ZAR': 'South Africa',
    'RUB': 'Russia',
    'TRY': 'Turkey'
}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trading Economics API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "countries": "/countries",
            "indicators": "/indicators/{country}",
            "currency_pairs": "/currency-pairs/{base}/{quote}",
            "interest_rates": "/interest-rates",
            "gdp_growth": "/gdp-growth",
            "inflation": "/inflation",
            "unemployment": "/unemployment"
        }
    }

@app.get("/countries", response_model=List[str])
async def get_available_countries():
    """Get list of available countries"""
    try:
        countries_data = te.getIndicatorData(output_type='df')
        if countries_data is not None and not countries_data.empty:
            countries = sorted(countries_data['Country'].unique().tolist())
            return countries
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
    
    # Fallback to major countries
    return list(CURRENCY_COUNTRY_MAP.values())

@app.get("/currencies", response_model=List[str])
async def get_available_currencies():
    """Get list of available currencies"""
    return list(CURRENCY_COUNTRY_MAP.keys())

@app.get("/indicators/{country}", response_model=CountryEconomicData)
async def get_country_indicators(country: str):
    """Get all economic indicators for a specific country"""
    try:
        data = get_country_economic_data(country)
        return data
    except Exception as e:
        logger.error(f"Error fetching indicators for {country}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data for {country}")

@app.get("/currency-pairs/{base}/{quote}", response_model=CurrencyPairData)
async def get_currency_pair_data(base: str, quote: str):
    """Get economic indicators for both countries in a currency pair"""
    base = base.upper()
    quote = quote.upper()
    
    if base not in CURRENCY_COUNTRY_MAP:
        raise HTTPException(status_code=404, detail=f"Currency {base} not supported")
    if quote not in CURRENCY_COUNTRY_MAP:
        raise HTTPException(status_code=404, detail=f"Currency {quote} not supported")
    
    base_country = CURRENCY_COUNTRY_MAP[base]
    quote_country = CURRENCY_COUNTRY_MAP[quote]
    
    try:
        base_data = get_country_economic_data(base_country)
        quote_data = get_country_economic_data(quote_country)
        
        return CurrencyPairData(
            base_currency=base,
            quote_currency=quote,
            base_country_data=base_data,
            quote_country_data=quote_data
        )
    except Exception as e:
        logger.error(f"Error fetching currency pair data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching currency pair data")

@app.get("/interest-rates", response_model=List[EconomicIndicator])
async def get_interest_rates(
    countries: Optional[List[str]] = Query(None, description="List of countries")
):
    """Get interest rates for specified countries or all major countries"""
    if not countries:
        countries = list(CURRENCY_COUNTRY_MAP.values())[:10]  # Top 10 major countries
    
    results = []
    for country in countries:
        data = safe_get_indicator_data(country, 'Interest Rate')
        if data:
            results.append(EconomicIndicator(**data))
    
    return results

@app.get("/gdp-growth", response_model=List[EconomicIndicator])
async def get_gdp_growth(
    countries: Optional[List[str]] = Query(None, description="List of countries")
):
    """Get GDP growth rates for specified countries or all major countries"""
    if not countries:
        countries = list(CURRENCY_COUNTRY_MAP.values())[:10]
    
    results = []
    for country in countries:
        data = safe_get_indicator_data(country, 'GDP Growth Rate')
        if data:
            results.append(EconomicIndicator(**data))
    
    return results

@app.get("/inflation", response_model=List[EconomicIndicator])
async def get_inflation_rates(
    countries: Optional[List[str]] = Query(None, description="List of countries")
):
    """Get inflation rates for specified countries or all major countries"""
    if not countries:
        countries = list(CURRENCY_COUNTRY_MAP.values())[:10]
    
    results = []
    for country in countries:
        data = safe_get_indicator_data(country, 'Inflation Rate')
        if data:
            results.append(EconomicIndicator(**data))
    
    return results

@app.get("/unemployment", response_model=List[EconomicIndicator])
async def get_unemployment_rates(
    countries: Optional[List[str]] = Query(None, description="List of countries")
):
    """Get unemployment rates for specified countries or all major countries"""
    if not countries:
        countries = list(CURRENCY_COUNTRY_MAP.values())[:10]
    
    results = []
    for country in countries:
        data = safe_get_indicator_data(country, 'Unemployment Rate')
        if data:
            results.append(EconomicIndicator(**data))
    
    return results

@app.get("/all-currency-pairs", response_model=List[CurrencyPairData])
async def get_all_major_currency_pairs():
    """Get economic data for all major currency pairs"""
    major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
    pairs = []
    
    # Generate major pairs (each currency against USD, EUR, GBP)
    base_currencies = ['USD', 'EUR', 'GBP']
    
    for base in base_currencies:
        for quote in major_currencies:
            if base != quote:
                try:
                    pair_data = await get_currency_pair_data(base, quote)
                    pairs.append(pair_data)
                except Exception as e:
                    logger.warning(f"Error fetching pair {base}/{quote}: {str(e)}")
                    continue
    
    return pairs

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Trading Economics connection
        test_data = te.getIndicatorData(country='United States', indicators='Interest Rate', output_type='df')
        api_status = "healthy" if test_data is not None else "degraded"
    except Exception as e:
        api_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "trading_economics_api": api_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)