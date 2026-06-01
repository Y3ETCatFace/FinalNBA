import pandas as pd
import xgboost as xgb
from sklearn.metrics import brier_score_loss, log_loss
import duckdb as db

con = db.connect('data/db/nba.db')
df = con.sql('SELECT * FROM training_data').df()

df.drop(columns=['team_id', 'game_id', 'is_back_to_back'], inplace = True)

X = df.drop(columns=["outcome"])
y = df["outcome"]

split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

model = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss")
model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]

print("LogLoss:", log_loss(y_test, probs))

model.save_model("model.json")
print("Model saved!")