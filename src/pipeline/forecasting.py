import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

DB_PATH = "data/air_quality.db"

def load_pm25_daily_series(region=None, recent_days=90):
    """Loads PM2.5 readings from SQLite, aggregated to daily means across
    all reporting stations. Aggregating to daily granularity smooths sensor
    noise and avoids extrapolating steep trends off a few hours of raw data.

    Args:
        region (str, optional): Filter to a specific station name.
        recent_days (int): Only keep days within the last N days of
            available data (relative to the most recent date found).

    Returns:
        pd.DataFrame: Columns [date, value, day_index], one row per day.
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT timestamp, value FROM air_quality_readings WHERE parameter = 'pm25'"
    params = []
    if region:
        query += " AND region = ?"
        params.append(region)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    df = df[df["timestamp"] != "unknown"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["date"] = df["timestamp"].dt.date

    daily = df.groupby("date", as_index=False)["value"].mean()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    cutoff = daily["date"].max() - pd.Timedelta(days=recent_days)
    daily = daily[daily["date"] >= cutoff].reset_index(drop=True)

    daily["day_index"] = (daily["date"] - daily["date"].min()).dt.days
    return daily

def train_forecast_model(df):
    """Trains a simple linear regression on day_index -> mean PM2.5 value.

    Args:
        df (pd.DataFrame): Must contain 'day_index' and 'value' columns.

    Returns:
        LinearRegression: Trained model.
    """
    X = df[["day_index"]]
    y = df["value"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def forecast_next_days(model, last_day_index, days_ahead=3):
    """Predicts PM2.5 values for the next N days.

    Args:
        model (LinearRegression): Trained forecasting model.
        last_day_index (int): The most recent day_index in the training data.
        days_ahead (int): Number of future days to forecast.

    Returns:
        np.ndarray: Predicted PM2.5 values for each future day.
    """
    future_days = pd.DataFrame(
        {"day_index": [last_day_index + i for i in range(1, days_ahead + 1)]}
    )
    return model.predict(future_days)

if __name__ == "__main__":
    df = load_pm25_daily_series(recent_days=90)
    print(f"Loaded {len(df)} daily PM2.5 averages spanning {df['date'].min().date()} to {df['date'].max().date()}")
    print(df.tail(10)[["date", "value"]])

    if len(df) < 2:
        print("\nNot enough distinct days of data to forecast a trend yet.")
    else:
        model = train_forecast_model(df)
        last_day = df["day_index"].max()
        forecast = forecast_next_days(model, last_day, days_ahead=3)

        print("\nForecasted daily mean PM2.5 for next 3 days:", forecast)