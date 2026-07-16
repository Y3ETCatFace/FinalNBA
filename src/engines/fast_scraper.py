from ollama import AsyncClient
import subprocess
import asyncio
from twscrape import gather
import json
from pathlib import Path
from random import uniform, random, randrange
from sys import stdout
from time import perf_counter
import numpy as np
import threading
import queue
from groq import Groq
import wave
import io
from twscrape import API
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
    api = API() 
    def __init__(self, prompt, sources, name, decline_words):
        self.prompt = prompt
        self.sources = sources
        self.name = name
        self.decline_words = decline_words
        self.last_tweet_id = {}
        
    async def confuse_and_wait(self):
        if random() <= .05:
            print('radnom')
            with open('data/runtime/random_searches.json') as f:
                searches = json.load(f)
            search = randrange(len(searches))
            await gather(Twitter.api.search(f"{search} lang:en", limit=20))
            await sleep(Twitter.time)
        else:
            await sleep(Twitter.time)
        
    async def add_account(self):
        with open('data/credentials/accounts.json', 'r') as f:
            accounts = json.load(f)
        for index, (email, meta) in enumerate(accounts.items()):
            print(f"adding account {index+1} to the pool.")
            await Twitter.api.pool.add_account_cookies(f"my_account{index+1}", f"auth_token={meta['auth_token']}; ct0={meta['ct0']}")
    
    async def update_id(self):
        subprocess.run(['ollama', 'pull', Twitter.llm_model])
        if not Path('data/runtime/x_ids.json').exists():    
            name_to_id = {}
        else:
            with open('data/runtime/x_ids.json', 'r') as f:
                name_to_id = json.load(f)
        for handle in self.sources:
            if handle in name_to_id:
                continue
            print(f"Fetching user ID for {handle}...")
            user = await Twitter.api.user_by_login(handle)
            print('Found!')
            await self.confuse_and_wait()
            name_to_id[handle] = user.id
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
        tweets = await gather(Twitter.api.user_tweets(name_to_id[handle], limit=num_tweets))
        if not tweets:
            print('tweets are none')
        return tweets
        
    async def get_ai_response(self, tweet):
        if any(word in tweet.lower() for word in self.decline_words):
            return 'Banned Word Detected'
        prompt = f'{self.prompt} Read ONLY the text below. TEXT: """{tweet}"""'
        response = await ask_ai(prompt)
        return response.upper()
        
    async def ping_account(self):
        for handle in self.sources:
            tweets = await asyncio.wait_for(self.get_last_tweets(handle), timeout=15)
            time = asyncio.create_task(self.confuse_and_wait())
            if tweets[0].id != self.last_tweet_id.get(handle):
                print(f"{handle} got something new")
                self.last_tweet_id[handle] = tweets[0].id
                return await self.get_ai_response(tweets[0].rawContent), time
            else:
                print(f"\n{handle} got nothing new {tweets[0].id}")
                return None, time
        return None, time

class Mentions:
    def __init__(self, webpage_url, groq_key, seconds):
        self.webpage_url = webpage_url
        self.groq_key = groq_key
        self.seconds = seconds
    
    def transcribe(self):
        model = Groq(api_key=self.groq_key)
        CHUNK_SIZE = 16000 * self.seconds
        audio_q = queue.Queue(maxsize=10)
        try:
            cmd = ["yt-dlp", "-g", "-f", "bestaudio/best", self.webpage_url]
            stream_url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            print(e)
        ffmpeg_cmd = [
            'ffmpeg',
            '-vn',                     # Block video packets
            '-i', stream_url,          # Pass the string variable directly here
            '-f', 's16le',             # Output raw 16-bit PCM bytes
            '-acodec', 'pcm_s16le',    
            '-ac', '1',                # Convert to mono
            '-ar', '16000',            # 16,000 Hz sample rate
            '-loglevel', 'quiet',      
            '-'                        # Target output to stdout
        ]
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**6)
        print("Listening live... Transcribing feed now:")
    
        def reader():
            while True:
                raw_bytes = process.stdout.read(CHUNK_SIZE)
                if not raw_bytes:
                    print('No Bites')
                    break
                audio_q.put(raw_bytes)
        threading.Thread(target=reader, daemon=True).start()
        raw_bytes = audio_q.get()
       
        with np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0 as audio_array:
            audio_energy = np.sqrt(np.mean(audio_array**2))
            if audio_energy < 0.002:  # If it's silent, skip the API call completely
                print('No energy')
                return None
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(raw_bytes)
        wav_buffer.seek(0)
        
        segments = model.audio.transcriptions.create(
            file=('file.wav', wav_buffer, 'audio/wav'),
            model="whisper-large-v3-turbo",
            language="en",
            temperature=0.0
        ) 
        return segments.text
        
if __name__ == "__main__":
    base_url = "https://www.twitch.tv/oiyorke"
