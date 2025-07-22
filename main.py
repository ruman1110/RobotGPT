from dotenv import load_dotenv

load_dotenv()  # This will load .env variables automatically

import discord
import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_KEY")
DISCORD_TOKEN = os.getenv("SECRET_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_KEY not found!")
if not DISCORD_TOKEN:
    raise ValueError("SECRET_KEY (Discord token) not found!")


class MyClient(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_histories = {}  

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user in message.mentions:
            user_id = str(message.author.id)
            prompt = message.clean_content.replace(f'@{self.user.name}', '').strip()

            
            history = self.user_histories.get(user_id, [])
            history.append({"role": "user", "content": prompt})

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://discord.com",
                "X-Title": "RonakBot-Memory"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": history,
                "temperature": 1,
                "max_tokens": 256
            }

            try:
                async with httpx.AsyncClient() as client_http:
                    response = await client_http.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    res_json = response.json()
                    reply = res_json['choices'][0]['message']['content'].strip()

                   
                    history.append({"role": "assistant", "content": reply})
                    self.user_histories[user_id] = history

                    await message.channel.send(reply)
                else:
                    await message.channel.send(f"API Error {response.status_code}: {response.text}")

            except Exception as e:
                await message.channel.send(f"An error occurred: {e}")



intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)