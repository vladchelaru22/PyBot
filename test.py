import os
from dotenv import load_dotenv
from nextcord.ext import commands
import aiohttp  # for gpt
import asyncio  # for music
import pyjokes
import random
from datetime import datetime, time
import requests
import json
from gtts import gTTS
import nextcord
from googleapiclient.discovery import build
import yt_dlp as youtube_dl

#importing variables
load_dotenv()
CHANNEL = 1102597234832453816
GOOGLE_API = os.getenv('GOOGLE_API')
TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')
api_key_weather = os.getenv('WEATHER_API_KEY')

# setting variables
intents = nextcord.Intents.all()
client = nextcord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


channel = bot.get_channel(CHANNEL)
#utc = datetime.timezone.utc
#time = datetime.time(hour=22, minute=12, tzinfo=utc)
# owm = pyowm.OWM('4b096846dea87214c945bf7a0158fe48')
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'PyBot is up and running!')
    channel = bot.get_channel(CHANNEL)
    await channel.send("Hello! PyBot is ready")
    bot.loop.create_task(quote_of_the_day())

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(CHANNEL)
    await channel.send(f"{member.mention} has joined the server")


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(CHANNEL)
    await channel.send(f"{member.mention} has left the server")


@bot.command(name='sum',help='Adds numbers')
async def add(context, *arr):
    sum = 0
    for i in arr:
        sum += int(i)
    await context.send(f"Sum: {sum}")

@bot.command(name='product',help='Solves the product of numbers')
async def product(context, *arr):
    product = 1
    for i in arr:
        product *= int(i)
    await context.send(f"Product: {product}")

@bot.command(name='divide',help='Solves the division of numbers')
async def divide(context, *arr):
    divide = int(arr[0])
    for i in arr[1:]:
        divide /= float(i)
    await context.send(f"Division: {divide}")


@bot.command(name='picture',help='Searches the web for what you ask it to')
async def picture(context,*,search):
    ran=random.randint(0,9)
    resource=build("customsearch","v1",developerKey=GOOGLE_API).cse()
    result= resource.list(
        q=f"{search}",cx="4550ab6116c05a3b2",searchType="image"
    ).execute()
    url=result["items"][ran]["link"]
    embed=nextcord.Embed(title=f"Your image: ({search.title()})")
    embed.set_image(url=url)
    await context.reply(embed=embed)

@bot.command(name='weather',help='Describes the weather in the city of your choosing')
async def weather(context, city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = city_name
    complete_url = base_url + "appid=" + api_key_weather + "&q=" + city
    response = requests.get(complete_url)
    res = response.json()
    info = res["main"]

    if response.status_code != 200:
        await context.reply("Invalid city name. Try again!")

    else:
        await context.reply(
            f'''Temperature in Celsius in {city_name} is : {int(info['temp'] - 273)}
How the temperature actually feels like : {int(info['feels_like'] - 273)}
Short description of the weather : {res['weather'][0]['description']}
Pressure : {info['pressure']}\nHumidity : {info['humidity']}%
            ''')

@bot.command(name='tts',help='Add a message and the bot will read it out loud')
async def tts(context, *args):
    text = " ".join(args)
    user = context.message.author
    if user.voice != None:
        try:
            vc = await user.voice.channel.connect()
        except:
            vc = context.voice_client

        sound = gTTS(text=text, lang="en", slow=False)
        sound.save("tts-audio.mp3")
        if vc.is_playing():
            vc.stop()
        source = nextcord.FFmpegPCMAudio("tts-audio.mp3")
        vc.play(source)

    else:
        await context.send("You need to be in a voice channel to run the command")


@bot.command(name='mute_bot', help='Bot will not listen to anymore commands except for "unmute"')
async def mute(ctx):
    guild = ctx.guild
    bot.muted_guilds.add(guild.id)
    await ctx.send('Bot is now muted and will not respond to further commands or messages.')


@bot.command(name='unmute',help='Bot will now listen to commands')
async def unmute(ctx):
    guild = ctx.guild
    if guild.id in bot.muted_guilds:
        bot.muted_guilds.remove(guild.id)
        await ctx.send('Bot is now unmuted and will respond to commands and messages again.')
    else:
        await ctx.send('Bot is not currently muted.')


@bot.check
def globally_block_commands(ctx):
    if ctx.guild and ctx.guild.id in bot.muted_guilds:
        if not ctx.command or ctx.command.name == 'unmute':
            return True  # Allow the unmute command even when the guild is muted
        return False  # Block all other commands when the guild is muted
    return True
bot.muted_guilds = set()  # Set to store muted guild IDs


@bot.command(name='quote',help='Delivers an inspirational quote')
async def quote(context):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    await context.send(quote)

async def quote_of_the_day():
    target_time = time(hour=18, minute=21, second=0)
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    while True:
        now = datetime.now().time()
        if now >= target_time:
            channel = bot.get_channel(CHANNEL)
            await channel.send(quote)
            await asyncio.sleep(86400)
        else:
            await asyncio.sleep(1)

@bot.command(name='joke',help='Delivers a "funny" joke')
async def joke(context):
    await context.send(pyjokes.get_joke())


@bot.command(name='remind',help='Add a reminder. Include the time in minutes + the reminder')
async def remind(context, time: int, *, msg):
    channel = bot.get_channel(CHANNEL)

    await context.send(f"Okay, I will remind you in {time} minutes.")
    await asyncio.sleep(time * 60)
    author = context.author
    await channel.send(f"Reminder: {msg} {author.mention}")


@bot.command(name='gpt',help='Interact with ChatGPT')
async def gpt(context: commands.Context, *, prompt: str):
    await context.send("Loading response from ChatGPT...")

    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "text-davinci-003",
            "prompt": prompt,
            "temperature": 0.5,
            "max_tokens": 200,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "best_of": 1
        }

        headers = {"Authorization": f"Bearer {API_KEY}"}

        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as resp:
            response = await resp.json()
            embed = nextcord.Embed(title="Chat GPT'S Response ", description=response["choices"][0]["text"])
            await context.reply(embed=embed)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    
@bot.command(name='leave', help='Make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
    
@bot.command(name='play', help='+youtube URL to play anything')
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(nextcord.FFmpegPCMAudio(executable="C:\\Users\\vladc\\Desktop\\PyBot\\ffmpeg\\bin\\ffmpeg.exe",
                                                  source=filename))
    await ctx.send('**Now playing:** {}'.format(filename))


@bot.command(name='pause', help='This command pauses the audio')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='resume', help='Resumes the audio')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")


@bot.command(name='stop', help='Stops the audio')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


bot.run(TOKEN)
print(client.guilds)
