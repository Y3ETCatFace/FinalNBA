from email import message
from ollama import chat
import subprocess
import asyncio
from twscrape import gather
import json
from pathlib import Path
from random import uniform, random, randrange
from sys import stdout
from time import perf_counter
import requests

#print(user.id, user.username, user.followersCount)


async def sleep(seconds):
    end = perf_counter() + seconds
    while True:
        remaining = end - perf_counter()
        if remaining <= 0:
            print(f"\r0.00\n", end='', flush=True)
            break
        print(f"\r{round(float(remaining), 2)} ", end = "", flush=True) 
        await asyncio.sleep(min(0.04, remaining))

class Twitter:
    time = uniform(5,7)
    def __init__(self, api, prompt, sources, name):
        self.api = api
        self.prompt = prompt
        self.sources = sources
        self.name = name
        
    async def confuse_and_wait(self):
        if random() < .02:
            with open('data/random_searches.json') as f:
                searches = json.load(f)
            search = randrange(len(searches))
            await asyncio.gather(gather(self.api.search(f"{search} lang:en", limit=20)), sleep(Twitter.time))
        else:
            await sleep(Twitter.time)
        
    async def add_account(self):
        with open('data/accounts.json', 'r') as f:
            accounts = json.load(f)
        for index, (email, meta) in enumerate(accounts.items()):
            print(f"adding account {index+1} to the pool.")
            await self.api.pool.add_account_cookies(f"my_account{index+1}", f"auth_token={meta['auth_token']}; ct0={meta['ct0']}")

    
    async def ensure_account(self):
        with open('data/random_searches.json') as f:
            searches = json.load(f)
        num = randrange(len(searches))
        tweets = await gather(self.api.search(f"{searches[num]} lang:en", limit=20))
        if not tweets:
            await self.add_account()
    
    async def update_id(self):
        if not Path('data/x_ids.json').exists():    
            name_to_id = {}
        else:
            with open('data/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        for handle in self.sources:
            if handle in name_to_id.get(self.name, {}):
                continue
            await self.confuse_and_wait()
            print(f"Fetching user ID for {handle}...")
            user = await self.api.user_by_login(handle)
            name_to_id.setdefault(self.name, {}).setdefault(handle, {})['id'] = user.id 
        with open(f'data/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
    
    async def get_last_tweets(self, handle, single_request=False, num_tweets=1):
        if single_request:
            self.update_id()
        with open('data/x_ids.json', 'r') as f:
            name_to_id = json.load(f)
        tweets = await gather(self.api.user_tweets(name_to_id[self.name][handle]['id'], limit=num_tweets))
        if tweets == None:
            raise
        return tweets
        
    async def get_ai_response(self, tweet):
        prompt = f'{self.prompt} Read ONLY the text below. TEXT: """{tweet}"""'
        try:
            response = chat(
                model='llama3.2:3b',
                messages=[{'role': 'user', 'content': prompt}],
            )
        except:
            subprocess.run(['ollama', 'pull', 'llama3.2:3b'], check=True)
            response = chat(
                model='llama3.2:3b',
                messages=[{'role': 'user', 'content': prompt}],
            )
        return response.message.content.upper()
    
    async def ping_account(self, name_to_id):
        while True:
            for handle in self.sources:
                tweets = await self.get_last_tweets(handle)
                account_info = name_to_id[self.name][handle]
                if tweets[0].id != account_info.get('last_tweet_id'):
                    print(f"{handle} got something new")
                    account_info['last_tweet_id'] = tweets[0].id
                    message_co = self.get_ai_response(tweets[0].rawContent)
                    messge, _ = await asyncio.gather(message_co, self.confuse_and_wait())
                    return messge
                else:
                    print(f"{handle} got nothing new")
                    await self.confuse_and_wait()

    

#print(user.id, user.username, user.followersCount) 
    
if __name__ == "__main__":
    async def main():
        from twscrape import API
        next_team = Twitter(
            api=API(), 
            sources = ["ShamsCharania", "KingJames"], 
            name = 'next_team',
            prompt = f'You are an NBA transaction extraction model. Analyze the news text and return EXACTLY one of two formats: 1. Player Full Name, Full Team Name (e.g., Lebron James, Utah Jazz) OR 2. sad. Rules for matching: Only return the player and team name if the text explicitly reports a completed or confirmed player move to a DIFFERENT NBA team. Treat these words as CONFIRMED: has agreed to a deal with, has agreed to a contract with, has agreed to sign with, is signing with, will sign with, has signed with, has been traded to, is being traded to, has been acquired by, is joining, is headed to, lands with, has reached an agreement with, finalizing a deal with. Return sad if the text contains rumors, speculation, or incomplete moves (e.g., interested in, considering, target, pursuing, expected to, could, may, might, likely, discussions, talks, negotiations, meetings, finalists, exploring, hopes to, plans to). Also return sad if: the player stays with the same team (re-signing/extension), no destination team is stated, or the text is about injuries, retirement, the draft, coaching, or waivers. CRITICAL FORMATTING: Do not wrap your response in markdown, code blocks, or backticks. Do not include any filler text, periods, or extra words. Output exactly one line with either Player Full Name, Full Team Name or sad.'
        )
        await next_team.ensure_account()
    asyncio.run(main())
