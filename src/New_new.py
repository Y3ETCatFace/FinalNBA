import asyncio
from engines.kalshi import Kalshi
from engines.fast_scraper import Twitter

async def main():
    message = "Only return TWO WORDS A FIRST NAME AND LAST ex. (John Adams) What is the NBA players full name in this title or rather what are the first two words of this sentence what is the name? Dont say anything else just his first and last name from this title I am about to show you:"
    test = Kalshi(
        'data/credentials/speed-2.pem', 
        '4beb2212-be89-4f64-b02b-fa7cf5ce5b5e', 
        'https://external-api.demo.kalshi.co')
        
    await test.create_event_name_map("kxnextteamnba".upper(), message, limit=200)

asyncio.run(main())