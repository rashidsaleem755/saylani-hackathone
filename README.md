# Data Engineering Hackathon: Real-Time Data Pipeline

A serverless data ingestion and processing pipeline using AWS services (Lambda, S3, SNS, SQS) to fetch, store, and process financial data from multiple sources.

## Data Sources
1. **Yahoo Finance**  
   - Fetch OHLCV (minute-level) for S&P 500 symbols using `yfinance` Python library.  
   - S&P 500 symbols sourced from [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).  

2. **CoinMarketCap**  
   - Scrape top 10 cryptocurrencies by market cap using `BeautifulSoup`/`Selenium`.  

3. **Open Exchange Rates**  
   - Fetch live forex data via API (requires [App ID](https://openexchangerates.org/)).

---

## Task 1: Data Acquisition (AWS Lambda + EventBridge)
### Steps
1. **Lambda Functions**  
   - Deploy 3 separate Lambda functions (Python) to fetch data from each source.  
   - Example: `lambda_yahoofinance`, `lambda_coinmarketcap`, `lambda_openexchangerates`.  

2. **EventBridge Scheduling**  
   - Trigger each Lambda **every minute** via EventBridge rules.  

3. **S3 Storage**  
   - **Bucket Name**: `data-hackathon-smit-{yourname}`  
   - **Path Structure**:  
     ```
     raw/
       ├── yahoofinance/YYYY/MM/DD/HHMM.{format}  
       ├── coinmarketcap/YYYY/MM/DD/HHMM.{format}  
       └── openexchangerates/YYYY/MM/DD/HHMM.{format}  
     ```  
   - **Metadata**: Each file must include `timestamp`, `source`, `symbol`, and `status`.  

---

## Task 2: Data Processing (SNS + SQS + Lambda)
### Pipeline Architecture
1. **S3 → SNS**  
   - SNS listens to S3 `PutObject` events.  
   - Filters events by metadata (`source`) and routes to relevant SQS FIFO queue.  

2. **SQS FIFO Queues**  
   - `yahoo-finance-queue.fifo`  
   - `coinmarketcap-queue.fifo`  
   - `openexchangerates-queue.fifo`  

3. **Lambda Processing**  
   - **Yahoo Finance**: Parses OHLCV → Snowflake.  
   - **CoinMarketCap**: Transforms data → S3 (`processed/`).  
   - **Open Exchange Rates**: Inserts forex rates → SQL Server.  

---

## Example Workflow
```plaintext
1. Lambda fetches data (every minute) → S3 (raw/).  
2. SNS routes S3 event → SQS queue.  
3. Lambda consumes queue → Processes data → Destination (Snowflake/S3/SQL Server).  