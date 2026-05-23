import duckdb as db
import pandas as pd

df = pd.read_csv('happytest.csv')

stat_cols = ['pts', 'reb', 'ast']

rolled = (
    df.groupby('team_id')[stat_cols]
    .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    .add_suffix('_last5')
)

df = pd.concat([df, rolled], axis=1)

df.to_csv('happytest2.csv', index=False)