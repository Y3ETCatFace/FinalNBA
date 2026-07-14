from ollama import AsyncClient
import subprocess
import asyncio
from twscrape import gather
import json
from pathlib import Path
from random import uniform, random, randrange
from sys import stdout
from time import perf_counter
import subprocess
import numpy as np
from faster_whisper import WhisperModel
import os
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
    llm_model = "qwen3:4b-instruct"
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
            with open('data/runtime/random_searches.json') as f:
                searches = json.load(f)
            search = randrange(len(searches))
            await gather(self.api.search(f"{search} lang:en", limit=20))
            await asyncio.sleep(Twitter.time)
        else:
            await sleep(Twitter.time)
        
    async def add_account(self):
        with open('data/credentials/accounts.json', 'r') as f:
            accounts = json.load(f)
        for index, (email, meta) in enumerate(accounts.items()):
            print(f"adding account {index+1} to the pool.")
            await self.api.pool.add_account_cookies(f"my_account{index+1}", f"auth_token={meta['auth_token']}; ct0={meta['ct0']}")
    
    async def update_id(self):
        if not Path('data/runtime/x_ids.json').exists():    
            name_to_id = {}
        else:
            with open('data/runtime/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        for handle in self.sources:
            if handle in name_to_id.get(self.name, {}):
                continue
            print(f"Fetching user ID for {handle}...")
            user = await self.api.user_by_login(handle)
            print('Found!')
            await self.confuse_and_wait()
            name_to_id.setdefault(self.name, {}).setdefault(handle, {})['id'] = user.id 
        with open(f'data/runtime/x_ids.json', 'w') as f:
            json.dump(name_to_id, f)
        self.name_to_id = name_to_id
    
    async def get_last_tweets(self, handle, single_request=False, num_tweets=1):
        if single_request:
            self.update_id()
        try:
            name_to_id = self.name_to_id
        except:
            with open('data/runtime/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        tweets = await gather(self.api.user_tweets(name_to_id[self.name][handle]['id'], limit=num_tweets))
        if not tweets:
            print('tweets are none')
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
                time = asyncio.create_task(self.confuse_and_wait())
                account_info = name_to_id[self.name][handle]
                if tweets[0].id != account_info.get('last_tweet_id'):
                    print(f"{handle} got something new")
                    account_info['last_tweet_id'] = tweets[0].id
                    return await self.get_ai_response(tweets[0].rawContent), time
                else:
                    print(f"\n{handle} got nothing new {tweets[0].id}")
                    return None, time
            except Exception as e:
                print(f'{handle} failed due to {e}')
                time = asyncio.create_task(self.confuse_and_wait())
                await time 
        return None, time

def get_stream_url_fast(webpage_url):
    try:
        cmd = ["yt-dlp", "-g", "-f", "bestaudio/best", webpage_url]
        stream_url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        return stream_url
    except subprocess.CalledProcessError:
        return None 
def transcribe(file_url):
    os.environ['HF_TOKEN'] = "fced3b403c0c8cc70f51b03ef3f4b37efa839369"
    model = WhisperModel("base.en", device="cpu", compute_type="int8")

    ffmpeg_cmd = [
        'ffmpeg',
        '-vn',                     # Block video packets
        '-i', file_url,          # Pass the string variable directly here
        '-f', 's16le',             # Output raw 16-bit PCM bytes
        '-acodec', 'pcm_s16le',    
        '-ac', '1',                # Convert to mono
        '-ar', '16000',            # 16,000 Hz sample rate
        '-loglevel', 'quiet',      
        '-'                        # Target output to stdout
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**6)

    CHUNK_SIZE = 32000 * 2

    print("Listening live... Transcribing feed now:")

    try:
        while True:
            # Pull 3 seconds worth of raw audio bytes from the pipe
            raw_bytes = process.stdout.read(CHUNK_SIZE)
            if not raw_bytes:
                break
            
            # Convert binary data to floating-point numbers for the AI model
            audio_array = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Feed the array to the transcriber
            segments, _ = model.transcribe(audio_array, beam_size=3)
            
            # Print results instantly as they happen
            for segment in segments:
                text = segment.text.strip()
                if text:
                    print(f"[Live Text]: {text}")
    except:
        pass
if __name__ == "__main__":
    base_url = "https://www.twitch.tv/flight23white"
    transcribe(get_stream_url_fast(base_url))
