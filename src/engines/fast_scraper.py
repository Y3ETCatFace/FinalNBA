from email import message
from ollama import chat
import subprocess
import asyncio
from twscrape import API, gather
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

class twitter:
    time = uniform(100,111)

    def __init__(self, api, prompt, sources, name):
        self.api = api
        self.prompt = prompt
        self.sources = sources
        self.name = name
    
    async def confuse_and_wait(self):
        if random() < .02:
            with open('random_searches.json') as f:
                searches = json.load(f)
            search = randrange(len(searches))
            await asyncio.gather(self.api.search(search), sleep(twitter.time))
        else:
            await sleep(twitter.time)
        
    async def add_account(self):
        with open('accounts.json', 'r') as f:
            accounts = json.load(f)
        for index, (email, meta) in enumerate(accounts.items()):
            print(f"adding account {index+1} to the pool.")
            await self.api.pool.add_account(
                username = meta['username'],
                email = email,
                password = meta['password'],
                cookies = f'auth_token={meta['auth_token']}; ct0={meta['ct0']}',
                email_password = ""
             )
    
    async def ensure_account(self):
        with open('random_searches.json') as f:
            searches = json.load(f)
        search = randrange(len(searches))
        search = await gather(self.api.search(search))
        if not search:
            await self.add_account()
    
    async def update_id(self):
        if not Path('x_ids.json').exists():    
            name_to_id = {}
        else:
            with open('x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        for handle in self.sources:
            if handle in name_to_id.get(self.name, {}):
                continue
            await self.confuse_and_wait()
            print(f"Fetching user ID for {handle}...")
            user = await self.api.user_by_login(handle)
            name_to_id.setdefault(self.name, {}).setdefault(handle, {})['id'] = user.id 
        with open(f'x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
    
    async def get_last_tweets(self, handle, single_request=False, num_tweets=1):
        if single_request:
            self.update_id()
        with open('x_ids.json', 'r') as f:
            name_to_id = json.load(f)
        tweets = await gather(self.api.user_tweets(name_to_id[self.name][handle]['id'], limit=num_tweets))
        if tweets == None:
            raise
        return tweets
        
    async def get_ai_response(self, tweets):
        prompt = f'{self.prompt} Read ONLY the text below. TEXT: """{tweets[0].rawContent}"""'
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
        return response.message.content
    
    async def ping_account(self):
        await self.ensure_account()
        await self.update_id()
        with open('x_ids.json', 'r') as f:
            name_to_id = json.load(f)
        try:
            while True:
                for handle in self.sources:
                    tweets = await self.get_last_tweets(handle)
                    account_info = name_to_id[self.name][handle]
                    if tweets[0].id != account_info.get('last_tweet_id'):
                        account_info['last_tweet_id'] = tweets[0].id
                        message_co = self.get_ai_response(tweets)
                        messge, _ = await asyncio.gather(message_co, self.confuse_and_wait())
                        return messge
                    else:
                        print(f"{handle} got nothing new")
                        await self.confuse_and_wait()
        finally:
            with open('x_ids.json', 'w') as f:
                json.dump(name_to_id, f)
    

#print(user.id, user.username, user.followersCount)

async def main():
    api = API()  # or API("accounts.db")    
    

    next_team = twitter(
        api=api, 
        sources = ["ShamsCharania", "KingJames"], 
        name = 'next_team',
        prompt = f'You are an NBA transaction extraction model. Return EXACTLY one of these outputs and nothing else: 1. <Player Full Name>, <City Team Name> 2. sad Return "<Player Full Name>, <City Team Name>" ONLY if the text explicitly reports a completed or market-confirmed player move to a DIFFERENT NBA team. Treat the following wording as CONFIRMED: - has agreed to a deal with - has agreed to a contract with - has agreed to sign with - is signing with - will sign with - has signed with - has been traded to - is being traded to - has been acquired by - is joining - is headed to - lands with - has reached an agreement with - finalizing a deal with - is finalizing a deal with Return "sad" if the text contains ANY rumor, speculation, or incomplete transaction, including wording such as: - interested in - considering - among those being considered - target - pursuing - expected to pursue - expected to sign - could - may - might - likely - discussions - talks - negotiations - meetings - finalists - candidates - monitoring - exploring - evaluating - hopes to - plans to Also return "sad" if: - the player remains with the same team (extension or re-signing), - no destination team is explicitly stated, - the news is about injuries, retirement, the draft, coaching, front office moves, waivers without a new team, or anything other than a player changing NBA teams. IMPORTANT: - Always return the player\'s FULL legal/common NBA name. - Always return the destination team\'s FULL CITY + TEAM NAME (e.g. "Los Angeles Lakers", "Golden State Warriors", "New York Knicks", "Oklahoma City Thunder"), never just the mascot or city. - Do not abbreviate player or team names. - Do not infer information from context. Only extract a move if the text explicitly states that the player is joining a specific new NBA team using confirmed transaction language. Output exactly one line with either: <Player Full Name>, <Full City Team Name> or sad',
   
    )
    await next_team.ping_account()

if __name__ == "__main__":
    asyncio.run(main())