import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from dataclasses import dataclass
import youtube_dl
import aiohttp  #for gpt
import asyncio  #for music
import time
import schedule 
import pyjokes


intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#CHANNEL=os.getenv('CHANNEL_ID')
CHANNEL=1102597234832453816
API_KEY='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'

voice_clients={}

yt_dl_opts={'format':'bestaudio/best'}
ytdl=youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options={'options':"-vn"}


#setting variables 
client = discord.Client(intents=intents)
bot=commands.Bot(command_prefix="!",intents=intents)


@bot.command()
async def joke(context):
    await context.send(pyjokes.get_joke())


#to do write time in hours or minutes or minutes
#tip comanda !remind "time" "task"
@bot.command()
async def remind(context, time:int, *, msg):

    channel=bot.get_channel(CHANNEL)

    await context.send(f"Okay, I will remind you in {time} minutes.")
    await asyncio.sleep(time*60)
    author=context.author
    await channel.send(f"Reminder: {msg} {author.mention}")



@bot.command()
async def play(msg):
    
    try :
        url=msg

        voice_client=await msg.author.voice.channel.connect()
        voice_clients[voice_client.guild.id]=voice_client

        loop=asyncio.get_event_loop()
        data= await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song=data['url']
        #player=discord.FFmpegPCMAudio(song,**ffmpeg_options, executable="/wsl.localhost/Ubuntu/home/smara/DiscordBot/ffmpeg/bin/ffmpeg.exe")
        player=discord.FFmpegPCMAudio(song,**ffmpeg_options, executable="C:\\Users\\smara\\Desktop\\ffmpeg\\bin\\ffmpeg.exe")
        #player=discord.FFmpegPCMAudio(song,**ffmpeg_options)
        voice_client.play(player)
    except Exception as err:
        print(err)


@bot.command()
async def gpt(context:commands.Context, *, prompt: str):
    
    await context.send("Loading response from ChatGPT...")
    
    async with aiohttp.ClientSession() as session:
        payload ={
            "model": "text-davinci-003",
            "prompt": prompt,
            "temperature" : 0.5,
            "max_tokens" : 200,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "best_of":1
        } 

        headers={"Authorization": f"Bearer {API_KEY}"}

        async with session.post("https://api.openai.com/v1/completions", json=payload , headers=headers) as resp:
            response = await resp.json()
            embed =discord.Embed(title="Chat GPT'S Response ", description=response["choices"][0]["text"])
            await context.reply(embed=embed)


@bot.event
async def on_ready():
    print(f' HELLO TO Discord!')
    channel=bot.get_channel(CHANNEL)
    await channel.send("Hello! Project Bot is ready")


@bot.command()
async def hello(context):
    await context.send("Hello!")


@bot.command()
async def add(context,*arr):
    sum=0
    for i in arr:
        sum+=i
    await context.send(f"Sum: {sum}")


bot.run(TOKEN)

print(client.guilds)

