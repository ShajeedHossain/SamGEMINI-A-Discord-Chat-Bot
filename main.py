import discord
import os
from google import genai
from google.genai import types

# Secrets
my_secret = os.environ['SECRET_KEY']
gemini_secret = os.environ['GEMINI_SECRET']

# GEMINI
gemini = genai.Client(api_key=gemini_secret)
sys_instruct = "You are a bot. Your name is Neko."

# Dictionary to store conversation history
chat_history = {}

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return  # Ignore messages from the bot itself

        if self.user in message.mentions:  # Respond only if mentioned
            channel_id = message.channel.id

            # Store conversation history per channel
            if channel_id not in chat_history:
                chat_history[channel_id] = []

            # Append the new message
            chat_history[channel_id].append(f"{message.author}: {message.content}")

            # Keep only the last 10 messages for context
            if len(chat_history[channel_id]) > 10:
                chat_history[channel_id].pop(0)

            # Create full conversation context
            context = "\n".join(chat_history[channel_id])

            # Get response from Gemini
            response = gemini.models.generate_content(
                model="gemini-2.0-flash",
                contents=context,  # Pass entire context
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.1,
                    system_instruction=sys_instruct))

            messageToSend = response.text


            # Clean response
            messageToSend = response.text.lstrip("Neko:").strip()
            
            # Append bot response to context
            chat_history[channel_id].append(f"Neko: {messageToSend}")

            await message.channel.send(messageToSend)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(my_secret)

