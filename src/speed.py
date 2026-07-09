from engines.fast_scraper import Twitter
from engines.kalshi import Kalshi
from twscrape import API
import asyncio
from tools.utils import nba_team_map
import json

async def main():     
    api = API()  # or API("accounts.db")    
    with open('data/x_ids.json', 'r') as f:
        name_to_id = json.load(f)

    next_team = Twitter(
        api=api, 
        sources = ["ShamsCharania"], 
        name = 'next_team',
        prompt = f'You are an NBA transaction extraction model. Analyze the news text and return EXACTLY one of two formats: 1. Player Full Name, Full Team Name (e.g., Lebron James, Utah Jazz) OR 2. sad. Rules for matching: Only return the player and team name if the text explicitly reports a completed or confirmed player move to a DIFFERENT NBA team. Treat these words as CONFIRMED: has agreed to a deal with, has agreed to a contract with, has agreed to sign with, is signing with, will sign with, has signed with, has been traded to, is being traded to, has been acquired by, is joining, is headed to, lands with, has reached an agreement with, finalizing a deal with. Return sad if the text contains rumors, speculation, or incomplete moves (e.g., interested in, considering, target, pursuing, expected to, could, may, might, likely, discussions, talks, negotiations, meetings, finalists, exploring, hopes to, plans to). Also return sad if: the player stays with the same team (re-signing/extension), no destination team is stated, or the text is about injuries, retirement, the draft, coaching, or waivers. CRITICAL FORMATTING: Do not wrap your response in markdown, code blocks, or backticks. Do not include any filler text, periods, or extra words. Output exactly one line with either Player Full Name, Full Team Name or sad.'
    )
    test = Kalshi(
        'data/speed-2.pem', 
        '4beb2212-be89-4f64-b02b-fa7cf5ce5b5e', 
        'https://external-api.demo.kalshi.co')

    await next_team.ensure_account()
    await next_team.update_id()
    
    try:
        while True:
            message = await next_team.ping_account(name_to_id)
            message_list = [item.strip() for item in message.split(",")]
            if 'LEBRON JAMES' in message_list:
                abrev = nba_team_map[message_list[1]]
                print(abrev)
                print(test.create_payload('ask', 100, f'KXNEXTTEAMNBA-26LJAM-{abrev}'))
                response = test.post('/portfolio/events/orders', test.create_payload('bid', 100, f'KXNEXTTEAMNBA-26LJAM-{abrev}'))
                if response.status_code == 201:
                    order = response.json()
                    print(f"Order placed successfully!")
                    print(f"Order ID: {order['order_id']}")
                    print(f"Remaining Count: {order['remaining_count']}")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                break
    finally:
        import datetime
        with open('data/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
        with open('data/log.txt', 'w') as f:
            f.write(str(int(datetime.datetime.now().timestamp() * 1000)))    

asyncio.run(main())