from engines.fast_scraper import Twitter
from engines.kalshi import Kalshi
from twscrape import API
import asyncio
from tools.utils import nba_team_map
import json
import datetime

async def main():     
    api = API()  # or API("accounts.db")   

    next_team = Twitter(
        api=api, 
        sources = ["ShamsCharania"],
        name="next_team",
        prompt = "Rule: Output exactly 'Nothing Important' by default. Only change this if the text explicitly confirms a player's team for next season, whether by new signing, trade, re-signing, or extension (the team does not need to be new). Only consider the FIRST player named in the text — ignore every other player mentioned, even in a trade involving multiple players. If that first player's team is confirmed, output exactly: Player Name, Team Name. If that first player is waived, released, bought out, or has no confirmed team, output exactly 'Nothing Important' — do not check any other player in the text. Examples: 'Celtics sign Holiday' -> 'Jrue Holiday, Boston Celtics'. 'Golden State Warriors trade Stephen Curry to Orlando Magic' -> 'Stephen Curry, Orlando Magic'. 'Nets re-sign Carter Ellis' -> 'Carter Ellis, Brooklyn Nets'. 'Nets waive Carter Ellis' -> 'Nothing Important'. 'Warriors waive Green' -> 'Nothing Important'.",
        decline_words=["offer sheet", "right to match", "days to match", "hours to match", "matching period", "in talks", "discussing", "exploring", "monitoring", "checking in on", "gauging interest", "expressed interest", "linked to", "eyeing", "mutual interest", "floated", "downplay", "denies", "denied", "shot down", "no truth to", "quashed", "not expected to be traded", "will finish out his contract", "bought out", 'buyout', "collapsed", "stalled", "unlikely", "remains unclear"]
    )
        
    test = Kalshi(
        'data/credentials/speed-2.pem', 
        '4beb2212-be89-4f64-b02b-fa7cf5ce5b5e', 
        'https://external-api.demo.kalshi.co')
    
    await next_team.add_account()
    await next_team.update_id()
    
    with open('data/runtime/temp_res.json', 'r') as f:
        player_to_ticker = json.load(f)
    with open('data/runtime/x_ids.json', 'r') as f:
        name_to_id = json.load(f)

    try:
        while True:
            message, time = await next_team.ping_account(name_to_id)
            if message and ',' in message:
                print(message)
                try:
                    message_list = [item.strip() for item in message.split(",")]
                    for i in range(0, len(message_list), 2):
                        abrev = nba_team_map[message_list[i+1]]
                        amount = 1200 if message_list[i].upper() == 'DEMAR DEROZAN' else 630 if message_list[i].upper() == "LEBRON JAMES" else 100
                        event_ticker = player_to_ticker[message_list[i]].upper()
                        response = test.create_order(side='bid', price='0.92', amount = amount, market_ticker=f'{event_ticker}-{abrev}')
                        if response.status_code == 201:
                            print(f"Order placed successfully!")
                        else:
                            print(f"Error: {response.status_code} - {response.text}")
                except:
                    print(f'\nList error or not mapped for {message_list}')
            else:
                print(message) if message else None
            await time
    finally:
        import datetime
        with open('data/runtime/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
        with open('data/log.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

asyncio.run(main())