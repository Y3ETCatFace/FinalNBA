# FinalNBA

News-reactor application for spotting NBA-related Kalshi contract opportunities and estimating expected value.

## Repository layout

```
accounts.db                 Twscrape account database — fixed location
data/
  accounts.json             Twitter-scraping login information
  random_searches.json      Decoy Twitter searches
  x_ids.json                Twitter source IDs and last-seen tweet IDs
  temp_res.json             Player-to-Kalshi-event ticker map
  speed.pem                 Kalshi authorization key
  speed-2.pem               Kalshi authorization key currently used by speed.py
  log.txt                   Reactor runtime timestamp/log
  raw_training_data/        Historical NBA CSV training inputs by season
src/
  main.py                   NBA data update / live query entry point
  speed.py                  Twitter-to-Kalshi reactor entry point
  engines/                  Twitter scraper and Kalshi trading client
  database/
    feature_pipeline/       SQL that builds model features
    live_queries/           SQL used for live expected-edge queries
    train.py                Model training script
  tools/                    Data collection, setup, features, config, utilities
  experiments/              Non-production scripts retained for reference
```

## Path preservation

The active code uses relative paths to the files directly under `data/` and to
`accounts.db`; those locations are deliberately preserved. No credentials,
training data, source code contents, or database files were modified.

`data/nba.db` is the DuckDB path expected by the training and utility code. It
is not currently present in this working tree, so it has not been created or
moved.
