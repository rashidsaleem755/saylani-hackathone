import json
import yfinance as yf
import pandas as pd
import boto3
from datetime import datetime
import requests
from bs4 import BeautifulSoup

your_name = "your-name"
s3_bucket = f"data-hackathon-smit-{your_name}"
sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_sp500_symbols(limit=10):
    try:
        response = requests.get(sp500_url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "constituents"})

        symbols = []
        for row in table.find_all("tr")[1:limit+1]:
            symbol = row.find_all("td")[0].text.strip()
            symbols.append(symbol)
        return symbols
    except Exception as e:
        raise RuntimeError(f"Failed to fetch S&P 500 symbols: {e}")

def get_finance_data(symbols, start_date, end_date, interval):
    result = {}
    for symbol in symbols:
        data = yf.download(tickers=symbol, start=start_date, end=end_date, interval=interval)
        if not data.empty:
            data = data.reset_index()
            data.columns = [str(col) for col in data.columns]

            if "Open" in data.columns and "Close" in data.columns:
                data["change_value"] = data["Close"] - data["Open"]
                data["change_percent"] = ((data["Close"] - data["Open"]) / data["Open"]) * 100

            result[symbol] = data.to_dict(orient="records")
    return result

def lambda_handler(event, context):
    try:
        symbols = event.get("symbols")
        if not symbols:
            symbols = get_sp500_symbols(10)

        start_date = event.get("start_date", "2024-01-01")
        end_date = event.get("end_date", "2024-01-10")
        interval = event.get("interval", "1d")

        data = get_finance_data(symbols, start_date, end_date, interval)

        now = datetime.utcnow()
        s3_key = now.strftime(f"raw/yahoofinance/%Y/%m/%d/%H%M.json")

        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=json.dumps(data, default=str),
            ContentType='application/json'
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Data fetched and stored to S3.",
                "symbols_used": symbols,
                "s3_path": f"s3://{s3_bucket}/{s3_key}"
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
