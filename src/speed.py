from engines.fast_scraper import Twitter
from engines.kalshi import Kalshi
from twscrape import API
import asyncio
from tools.utils import nba_team_map
import json

async def main():     
    api = API()  # or API("accounts.db")   

    next_team = Twitter(
        api=api, 
        sources = ["ShellyCooper26"], 
        name="next_team",
        prompt = "Rule Your default output for all text is exactly Nothing Important You must only change this output to the format Player Name, Team Name if the text explicitly confirms a completed signing or trade where a player joins a team If a player is being waived released bought out or leaving a team without a team confirmed you must output exactly Nothing Important Never extract a player name or use a comma if they are just leaving a team or if the team is missing Examples Text Celtics sign Jrue Holiday Output Jrue Holiday, Boston Celtics Text Nets waive Carter Ellis Output Nothing Important Text Suns part ways with Jordan Pierce Output Nothing Important",
        decline_words=["offer sheet", "right to match", "days to match", "hours to match", "matching period", "in talks", "discussing", "exploring", "monitoring", "checking in on", "gauging interest", "expressed interest", "linked to", "eyeing", "mutual interest", "floated", "downplay", "denies", "denied", "shot down", "no truth to", "quashed", "not expected to be traded", "will finish out his contract", "bought out", 'buyout', "collapsed", "stalled", "unlikely", "remains unclear"]
    )
        
    test = Kalshi(
        'data/speed-2.pem', 
        '4beb2212-be89-4f64-b02b-fa7cf5ce5b5e', 
        'https://external-api.demo.kalshi.co')
    
    await next_team.add_account()
    await next_team.update_id()
    
    with open('data/temp_res.json', 'r') as f:
        player_to_ticker = json.load(f)
    with open('data/x_ids.json', 'r') as f:
        name_to_id = json.load(f)

    try:
        while True:
            message, time = await next_team.ping_account(name_to_id)
            if message and ',' in message:
                try:
                    message_list = [item.strip() for item in message.split(",")]
                    abrev = nba_team_map[message_list[1]]
                    event_ticker = player_to_ticker[message_list[0]]
                    response = test.create_order(side='bid', price='0.92', amount = 100, market_ticker=f'{event_ticker}-{abrev}')
                    if response.status_code == 201:
                        print(f"Order placed successfully!")
                    else:
                        print(f"Error: {response.status_code} - {response.text}")
                except:
                    print(f'\nList error or not mapped for {message_list}')
            await time
    finally:
        import datetime
        with open('data/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
        with open('data/log.txt', 'w') as f:
            f.write(str(int(datetime.datetime.now().timestamp() * 1000)))    

asyncio.run(main())