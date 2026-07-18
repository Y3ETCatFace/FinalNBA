from engines.fast_scraper import Twitter, Mentions
from engines.kalshi import Kalshi
from twscrape import API
import asyncio
from tools.utils import nba_team_map
import json
import datetime

real = Kalshi(
    'data/credentials/final.pem',
    'e0aa7334-2f4a-481c-8ba6-a3773e57599c',
    'https://external-api.kalshi.com'
)

async def next_team():     
    next_team = Twitter(
        sources = ["ShamsCharania"],
        name="next_team",
        prompt = "Rule: Output exactly 'Nothing Important' by default. Only change this if the text explicitly confirms a player's team for next season, whether by new signing, trade, re-signing, or extension (the team does not need to be new). Only consider the FIRST player named in the text — ignore every other player mentioned, even in a trade involving multiple players. If that first player's team is confirmed, output exactly: Player Name, Team Name. If that first player is waived, released, bought out, or has no confirmed team, output exactly 'Nothing Important' — do not check any other player in the text. Examples: 'Celtics sign Holiday' -> 'Jrue Holiday, Boston Celtics'. 'Golden State Warriors trade Stephen Curry to Orlando Magic' -> 'Stephen Curry, Orlando Magic'. 'Nets re-sign Carter Ellis' -> 'Carter Ellis, Brooklyn Nets'. 'Nets waive Carter Ellis' -> 'Nothing Important'. 'Warriors waive Green' -> 'Nothing Important'.",
        decline_words=["offer sheet", "right to match", "days to match", "hours to match", "matching period", "in talks", "discussing", "exploring", "monitoring", "checking in on", "gauging interest", "expressed interest", "linked to", "eyeing", "mutual interest", "floated", "downplay", "denies", "denied", "shot down", "no truth to", "quashed", "not expected to be traded", "will finish out his contract", "bought out", 'buyout', "collapsed", "stalled", "unlikely", "remains unclear"]
    )
    map_prompt = "Only return TWO WORDS A FIRST NAME AND LAST ex. (John Adams) What is the NBA players full name in this title or rather what are the first two words of this sentence what is the name? Dont say anything else just his first and last name from this title I am about to show you:"
    player_to_ticker = await real.create_event_name_map("kxnextteamnba".upper(), limit=200, map_prompt=map_prompt)
    
    try:
        while True:
            message, time = await next_team.ping_account()
            if message and ',' in message:
                print(message)
                try:
                    message_list = [item.strip() for item in message.split(",")]
                    for i in range(0, len(message_list), 2):
                        abrev = nba_team_map[message_list[i+1]]
                        amount = 1200 if message_list[i].upper() == 'DEMAR DEROZAN' else 630 if message_list[i].upper() == "LEBRON JAMES" else 100
                        event_ticker = player_to_ticker[message_list[i]].upper()
                        response = real.create_order(side='bid', price='0.92', amount = amount, market_ticker=f'{event_ticker}-{abrev}')
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
        with open('data/log.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

async def mentions():
    urls = {}
    while True:
        url = input("Enter any url then space followed by the event ticker or enter done if done: ")
        if url.lower() == 'done':
            break
        url.split
        

    mentions = Mentions(
            webpage_urls=urls,
            seconds=5
            )
    async def idk(index):
        segments = []
        while True:
            segment = mentions.transcribe(index)
            segments.append(segment)
            if len(segments) > 2:
                segments.pop(0)
            text = " ".join(segments)
    for index, url in enumerate(urls):
        asyncio.create_task(idk(index))
asyncio.run(next_team())