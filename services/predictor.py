import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import timedelta

FORECAST_DAYS = 180  # 6 months

def predict_prices(csv_path):
    # Load CSV
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Convert Stay Date
    df["Stay Date"] = pd.to_datetime(df["Stay Date"], dayfirst=True)

    # Target
    target = "ADR"

    # Features
    features = [
        "Day Of Week",
        "Room Type Name",
        "Room Type Category",
        "Market Segment",
        "Source Code",
        "Rate Plan",
        "Room Sold",
        "Occupancy"
    ]

    df = df[features + ["Stay Date", target]].dropna()

    # Encode categorical columns
    encoders = {}
    categorical_cols = [
        "Day Of Week",
        "Room Type Name",
        "Room Type Category",
        "Market Segment",
        "Source Code",
        "Rate Plan"
    ]

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df[features]
    y = df[target]

    # Train model
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        random_state=42
    )
    model.fit(X, y)

    # Determine forecast start date (today)
    last_date = df["Stay Date"].max()
    start_date = last_date + timedelta(days=1)

    predictions = []

    # Loop future dates
    for day in range(FORECAST_DAYS):
        forecast_date = start_date + timedelta(days=day)
        day_name = forecast_date.strftime("%A")

        # Encode day of week
        day_encoded = encoders["Day Of Week"].transform([day_name])[0]

        for room_type in encoders["Room Type Name"].classes_:
            room_encoded = encoders["Room Type Name"].transform([room_type])[0]

            room_df = df[df["Room Type Name"] == room_encoded]

            # Build future feature vector
            sample = {
                "Day Of Week": day_encoded,
                "Room Type Name": room_encoded,
                "Room Type Category": int(room_df["Room Type Category"].mode()[0]),
                "Market Segment": int(room_df["Market Segment"].mode()[0]),
                "Source Code": int(room_df["Source Code"].mode()[0]),
                "Rate Plan": int(room_df["Rate Plan"].mode()[0]),
                "Room Sold": room_df["Room Sold"].mean(),
                "Occupancy": room_df["Occupancy"].mean()
            }

            sample_df = pd.DataFrame([sample])
            predicted_adr = model.predict(sample_df)[0]

            predictions.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day_of_week": day_name,
                "room_type": room_type,
                "predicted_adr": round(predicted_adr, 2)
            })

    return predictions
