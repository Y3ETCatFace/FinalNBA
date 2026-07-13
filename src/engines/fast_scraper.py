from ollama import AsyncClient
import subprocess
import asyncio
from twscrape import gather
import json
from pathlib import Path
from random import uniform, random, randrange
from sys import stdout
from time import perf_counter
#print(user.id, user.username, user.followersCount)

async def ask_ai(prompt):
    try:
        response = await AsyncClient().chat(
            model=Twitter.llm_model,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.0,
                'num_predict': 15  # This is Ollama's parameter for max_tokens
            }
        )
    except:
        subprocess.run(['ollama', 'pull', Twitter.llm_model])
        response = await AsyncClient().chat(
            model=Twitter.llm_model,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.0,
                'num_predict': 15  # This is Ollama's parameter for max_tokens
            }
        )
    return response.message.content

async def sleep(seconds):
    end = perf_counter() + seconds
    while True:
        remaining = end - perf_counter()
        if remaining <= 0:
            print(f"\rTime till next request: 0.00  ", end="", flush=True)
            break
        print(f"\rTime till next request: {round(float(remaining), 2)}  ", end="", flush=True)
        await asyncio.sleep(min(uniform(0.05, 0.09), remaining))

class Twitter:
    time = uniform(5,7)
    llm_model = "phi4-mini:3.8b"
    def __init__(self, api, prompt, sources, name, decline_words):
        self.api = api
        self.prompt = prompt
        self.sources = sources
        self.name = name
        self.decline_words = decline_words
        self.name_to_id = None
        
    async def confuse_and_wait(self):
        if random() <= .05:
            print('radnom')
            with open('data/random_searches.json') as f:
                searches = json.load(f)
            search = randrange(len(searches))
            await gather(self.api.search(f"{search} lang:en", limit=20))
            await asyncio.sleep(Twitter.time)
        else:
            await sleep(Twitter.time)
        
    async def add_account(self):
        with open('data/accounts.json', 'r') as f:
            accounts = json.load(f)
        for index, (email, meta) in enumerate(accounts.items()):
            print(f"adding account {index+1} to the pool.")
            await self.api.pool.add_account_cookies(f"my_account{index+1}", f"auth_token={meta['auth_token']}; ct0={meta['ct0']}")
    
    async def update_id(self):
        if not Path('data/x_ids.json').exists():    
            name_to_id = {}
        else:
            with open('data/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        for handle in self.sources:
            if handle in name_to_id.get(self.name, {}):
                continue
            print(f"Fetching user ID for {handle}...")
            user = await self.api.user_by_login(handle)
            print('Found!')
            name_to_id.setdefault(self.name, {}).setdefault(handle, {})['id'] = user.id 
        with open(f'data/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
        self.name_to_id = name_to_id
        await self.confuse_and_wait()
    
    async def get_last_tweets(self, handle, single_request=False, num_tweets=1):
        if single_request:
            self.update_id()
        try:
            name_to_id = self.name_to_id
        except:
            with open('data/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        tweets = await gather(self.api.user_tweets(name_to_id[self.name][handle]['id'], limit=num_tweets))
        if tweets == None:
            raise
        return tweets
        
    async def get_ai_response(self, tweet):
        if any(word in tweet.lower() for word in self.decline_words):
            return 'Banned Word Detected'
        prompt = f'{self.prompt} Read ONLY the text below. TEXT: """{tweet}"""'
        response = await ask_ai(prompt)
        return response.upper()
        
    async def ping_account(self, name_to_id):
        for handle in self.sources:
            try:
                tweets = await asyncio.wait_for(self.get_last_tweets(handle), timeout=15)
            except:
                continue
            time = asyncio.create_task(self.confuse_and_wait())
            account_info = name_to_id[self.name][handle]
            if tweets[0].id != account_info.get('last_tweet_id'):
                print(f"{handle} got something new")
                account_info['last_tweet_id'] = tweets[0].id
                return await self.get_ai_response(tweets[0].rawContent), time
            else:
                print(f"\n{handle} got nothing new ({tweets[0].id})")
                return None, time

#print(user.id, user.username, user.followersCount) 
    
if __name__ == "__main__":
    async def main():
        from twscrape import API
        next_team = Twitter(
            api=API(), 
            sources = ["ShamsCharania", "KingJames"], 
            name = 'next_team',
            prompt = "You are a ZERO-TOLERANCE NBA transaction verification engine. You are NOT a news summarizer. You are a binary legal-certainty gate. A single wrong output causes irreversible financial loss. Your default state is DOUBT. HOWEVER, VERIFIED NBA INSIDER REPORTS (such as ESPN, Shams Charania, Adrian Wojnarowski, The Athletic, official NBA/team announcements, or other verified league reporters) stating a player HAS AGREED TO, HAS AGREED TO TERMS, HAS REACHED AN AGREEMENT, HAS SIGNED, HAS BEEN TRADED, HAS FINALIZED A DEAL, or HAS GIVEN HIS COMMITMENT represent COMPLETED TRANSACTIONS for this task even if league paperwork, physicals, moratorium restrictions, or official press releases are still pending. 'Sources tell ESPN', 'sources tell Shams', 'sources confirm', and similar attribution DO NOT make the transaction speculative. They indicate a completed agreement unless the text explicitly contains a STOP-LIST phrase. [RULE 0 -- READ THE ENTIRE TEXT BEFORE ANSWERING] Read the ENTIRE input before deciding. Later clauses override earlier ones. [RULE 1 -- STOP-LIST] If the text contains ANY indication the transaction is unresolved, speculative, conditional, reversible, or incomplete, immediately output exactly: sad. STOP phrases include: offer sheet, restricted free agent, RFA, hours to match, right to match, matching period, discussing, discussion, talks, negotiating, negotiating with, exploring, considering, eyeing, interested in, mutual interest, expected to sign, plans to sign, intends to sign, could sign, may sign, likely to sign, pursuing, targeting, monitoring, linked to, requested a trade, wants out, weighing options, stalled, collapsed, fell through, unlikely, no deal imminent, remains unclear, waived, released, bought out without a confirmed destination, denied, downplayed, no truth to, not expected to be traded, will finish out his contract, remains with the team for now. If ANY STOP phrase appears anywhere, output exactly: sad. [RULE 2 -- COMPLETED TRANSACTION] Otherwise, if the text states a player HAS AGREED TO A DEAL, HAS AGREED TO TERMS, HAS REACHED AN AGREEMENT, HAS SIGNED, HAS BEEN TRADED, HAS BEEN ACQUIRED, HAS FINALIZED A DEAL, HAS FINALIZED A TRADE, TRADE IS DONE, TRADE IS COMPLETE, TEAM RECEIVED THE PLAYER'S COMMITMENT, or equivalent completed language, AND both the player and destination team are identified, output exactly: PlayerName, TeamName. Treat 'has agreed to a two-year deal', 'sources tell ESPN', and 'received the commitment tonight' as COMPLETED transactions, NOT speculation. [RULE 3 -- RETENTION] If instead the player has signed an extension, exercised a player option, had a team option exercised, or had salary guaranteed, output: PlayerName, CurrentTeamName. [RULE 4 -- DEFAULT] Otherwise output exactly: sad. Output ONLY either 'PlayerName, TeamName' or 'sad'. No explanation, reasoning, markdown, punctuation, or extra words."
        )
    asyncio.run(main())
