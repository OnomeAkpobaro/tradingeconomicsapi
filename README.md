# Trading Economics FastAPI

A professional-grade REST API service that provides seamless access to global economic indicators through Trading Economics data. Built with FastAPI for high performance and automatic API documentation.

## 🚀 Features

- **Comprehensive Economic Data**: Access interest rates, GDP growth, inflation rates, and unemployment data
- **Currency Pair Analysis**: Get economic indicators for both countries in any major currency pair
- **Real-time Data**: Fetch the latest economic indicators from Trading Economics
- **High Performance**: Built with FastAPI for optimal speed and scalability
- **Interactive Documentation**: Automatic OpenAPI/Swagger documentation
- **Error Resilience**: Robust error handling with graceful fallbacks
- **CORS Enabled**: Ready for cross-origin requests from web applications

## 📊 Supported Indicators

| Indicator | Description | Coverage |
|-----------|-------------|----------|
| Interest Rate | Central bank policy rates | 25+ countries |
| GDP Growth Rate | Quarterly economic growth | 25+ countries |
| Inflation Rate | Consumer price inflation | 25+ countries |
| Unemployment Rate | Labor market statistics | 25+ countries |

## 💰 Supported Currencies

**Major Currencies**: USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD  
**European**: SEK, NOK, DKK, PLN, CZK, HUF  
**Asia-Pacific**: SGD, HKD, KRW, CNY, INR  
**Emerging Markets**: BRL, MXN, ZAR, RUB, TRY

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Trading Economics API key ([Get one here](https://tradingeconomics.com/api/))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/trading-economics-api.git
   cd trading-economics-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   ```bash
   export TRADING_ECONOMICS_API_KEY='your_api_key_here'
   # Or create a .env file with: TRADING_ECONOMICS_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📋 Requirements

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
tradingeconomics==0.3.2
pandas==2.1.3
python-dotenv==1.0.0
pydantic==2.5.0
```

## 🔗 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/docs` | Interactive API documentation |
| GET | `/health` | Health check and API status |

### Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/countries` | List all supported countries |
| GET | `/currencies` | List all supported currencies |
| GET | `/indicators/{country}` | All economic indicators for a country |
| GET | `/currency-pairs/{base}/{quote}` | Economic data for currency pair |
| GET | `/all-currency-pairs` | Data for all major currency pairs |

### Indicator-Specific Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interest-rates` | Interest rates for specified countries |
| GET | `/gdp-growth` | GDP growth rates for specified countries |
| GET | `/inflation` | Inflation rates for specified countries |
| GET | `/unemployment` | Unemployment rates for specified countries |

## 📖 Usage Examples

### Get Currency Pair Data

```bash
curl "http://localhost:8000/currency-pairs/USD/EUR"
```

```python
import requests

response = requests.get("http://localhost:8000/currency-pairs/USD/EUR")
data = response.json()

print(f"USD Interest Rate: {data['base_country_data']['interest_rate']['value']}%")
print(f"EUR Interest Rate: {data['quote_country_data']['interest_rate']['value']}%")
```

### Get Multiple Country Indicators

```bash
curl "http://localhost:8000/interest-rates?countries=United%20States&countries=Canada&countries=United%20Kingdom"
```

```javascript
const axios = require('axios');

async function getInterestRates() {
  const response = await axios.get('http://localhost:8000/interest-rates', {
    params: {
      countries: ['United States', 'Canada', 'United Kingdom']
    }
  });
  
  response.data.forEach(rate => {
    console.log(`${rate.country}: ${rate.value}%`);
  });
}
```

### Get All Indicators for a Country

```python
import requests

response = requests.get("http://localhost:8000/indicators/United States")
data = response.json()

print(f"Country: {data['country']}")
print(f"Interest Rate: {data['interest_rate']['value']}%")
print(f"GDP Growth: {data['gdp_growth']['value']}%")
print(f"Inflation: {data['inflation_rate']['value']}%")
print(f"Unemployment: {data['unemployment_rate']['value']}%")
```

## 📄 Response Format

### Economic Indicator

```json
{
  "country": "United States",
  "indicator": "Interest Rate",
  "value": 5.25,
  "previous_value": 5.00,
  "last_update": "2024-12-15T10:30:00",
  "unit": "%",
  "frequency": "Monthly"
}
```

### Currency Pair Data

```json
{
  "base_currency": "USD",
  "quote_currency": "EUR",
  "base_country_data": {
    "country": "United States",
    "interest_rate": {
      "country": "United States",
      "indicator": "Interest Rate",
      "value": 5.25,
      "previous_value": 5.00,
      "last_update": "2024-12-15T10:30:00",
      "unit": "%",
      "frequency": "Monthly"
    },
    "gdp_growth": { /* ... */ },
    "inflation_rate": { /* ... */ },
    "unemployment_rate": { /* ... */ },
    "last_updated": "2024-12-15T10:30:00"
  },
  "quote_country_data": {
    "country": "Euro Area",
    /* Similar structure for EUR area data */
  }
}
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADING_ECONOMICS_API_KEY` | Your Trading Economics API key | `guest:guest` |
| `PORT` | Port number for the application | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🔒 API Key Management

### Getting Your API Key

1. Visit [Trading Economics API](https://tradingeconomics.com/api/)
2. Create an account and subscribe to a plan
3. Access your API key from the dashboard

### Setting Up Authentication

**Production (Environment Variable)**:
```bash
export TRADING_ECONOMICS_API_KEY='your_production_key'
```

**Development (.env file)**:
```
TRADING_ECONOMICS_API_KEY=your_development_key
```

**Testing (Guest Access)**:
```
TRADING_ECONOMICS_API_KEY=guest:guest
```
*Note: Guest access returns sample data only*

## 📊 Rate Limits

- **Free Tier**: 500 requests/month
- **Starter**: 10,000 requests/month
- **Professional**: 100,000 requests/month
- **Enterprise**: Custom limits

The API automatically handles rate limiting with appropriate error responses.

## 🛠️ Development

### Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

### Code Formatting

```bash
pip install black isort
black main.py
isort main.py
```

### Adding New Indicators

1. Update the `indicators` dictionary in `get_country_economic_data()`
2. Add the corresponding endpoint function
3. Update the response models if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [FastAPI Docs](https://fastapi.tiangolo.com/)
- **Trading Economics API**: [API Documentation](https://docs.tradingeconomics.com/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/trading-economics-api/issues)

## 🙏 Acknowledgments

- [Trading Economics](https://tradingeconomics.com/) for providing the economic data API
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

---

**⭐ Star this repository if you find it useful!**