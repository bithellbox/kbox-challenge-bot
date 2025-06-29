import discord
from discord.ext import commands
import json
import os  # Add this near the top if it’s not already there

# Set up intents and the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# File to store challenges
CHALLENGE_FILE = "challenges.json"
# Channel ID where submissions will be posted publicly
PUBLIC_CHANNEL_ID = 123456789012345678  # Replace with your actual channel ID

# Ensure the challenge file exists
if not os.path.exists(CHALLENGE_FILE):
    with open(CHALLENGE_FILE, 'w') as f:
        json.dump([], f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def submitchallenge(ctx):
    try:
        await ctx.author.send("Let's submit your challenge! What game is this for?")

        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        game = await bot.wait_for('message', check=check, timeout=120.0)
        await ctx.author.send("Awesome! Now describe the challenge in detail.")

        challenge = await bot.wait_for('message', check=check, timeout=120.0)
        await ctx.author.send("Any weird rules or restrictions?")

        rules = await bot.wait_for('message', check=check, timeout=120.0)
        await ctx.author.send("Would you like a shout-out if Kevin uses this challenge? (yes/no)")

        shoutout = await bot.wait_for('message', check=check, timeout=60.0)
        shoutout_response = shoutout.content.lower().strip()
        show_name = False
        if shoutout_response == "yes":
            await ctx.author.send("What name or username should we credit?")
            name = await bot.wait_for('message', check=check, timeout=60.0)
            show_name = name.content.strip()
        else:
            show_name = False

        # Store the submission
        with open(CHALLENGE_FILE, 'r') as f:
            data = json.load(f)

        entry = {
            "user": ctx.author.name,
            "game": game.content,
            "challenge": challenge.content,
            "rules": rules.content,
            "shoutout": bool(show_name),
            "name": show_name if show_name else "Anonymous"
        }

        data.append(entry)

        with open(CHALLENGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        await ctx.author.send("✅ Challenge submitted! Thanks, Kevin will suffer in due time.")

        # Post publicly in the channel
        public_channel = bot.get_channel(PUBLIC_CHANNEL_ID)
        if public_channel:
            embed = discord.Embed(title=f"🎮 New Challenge Submitted!", color=0xff5733)
            embed.add_field(name="Game", value=game.content, inline=False)
            embed.add_field(name="Challenge", value=challenge.content, inline=False)
            embed.add_field(name="Rules", value=rules.content, inline=False)
            if show_name:
                embed.set_footer(text=f"Submitted by {show_name}")
            else:
                embed.set_footer(text="Submitted anonymously")

            await public_channel.send(embed=embed)

    except Exception as e:
        await ctx.author.send("❌ Something went wrong or timed out. Please try again.")
        print(f"Error during challenge submission: {e}")

# Run the bot
import os  # Add this near the top if it’s not already there

bot.run(os.getenv("BOT_TOKEN"))

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Minimal web server to keep Render happy
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_webserver():
    server = HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8000))), Handler)
    server.serve_forever()

# Start web server in background thread
threading.Thread(target=run_webserver, daemon=True).start()

# Then start your bot
bot.run(os.getenv("BOT_TOKEN"))
