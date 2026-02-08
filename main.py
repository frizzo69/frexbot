import discord
import os
import asyncio
from discord.ext import commands

# 1. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix="-", intents=intents)

# 2. Function to load cogs
async def load_extensions():
    # Looks for files in the 'cogs' folder ending in .py
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"✅ Loaded extension: {filename}")

@bot.event
async def on_ready():
    print(f'🤖 Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def main():
    async with bot:
        await load_extensions()
        # Get token from Replit Secrets (Environment Variables)
        try:
            await bot.start(os.environ['TOKEN'])
        except KeyError:
            print("❌ Error: 'TOKEN' not found in Secrets.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle manual stop gracefully
        pass
