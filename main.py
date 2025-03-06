import discord
from discord.ext import commands
import requests
import os
import json
from dotenv import load_dotenv
import asyncio
import subprocess

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ZONE_ID = os.getenv("ZONE_ID")
DOMAIN = os.getenv("DOMAIN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUBDOMAIN_FILE = "subdomains.json"

# Fungsi cek proxy Growtopia
def check_proxy(ip, port, username, password):
    proxy = f"{username}:{password}@{ip}:{port}"
    
    # Cek Growtopia login API
    login_url = "https://login.growtopiagame.com/player/login/dashboard"
    headers = {
        "User-Agent": "UbiServices_SDK_2022.Release.9_PC64_ansi_static"
    }
    data = "version=5.07&platform=0&protocol=214"
    
    login_cmd = f'curl -x socks5://{proxy} -d "{data}" -H "User-Agent: {headers["User-Agent"]}" -s -o /dev/null -w "%{{http_code}}" {login_url}'
    login_process = subprocess.Popen(login_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    login_output, _ = login_process.communicate()
    
    login_status = login_output.decode().strip()
    gt_status = "✅ **GT Unblocked**" if login_status not in ["403", "404", "502"] else "❌ **GT Blocked**"

    # Cek Growtopia server_data.php
    server_data_url = "https://growtopia1.com/growtopia/server_data.php"
    server_data_cmd = f'curl -x socks5://{proxy} -s -o /dev/null -w "%{{http_code}}" {server_data_url}'
    server_data_process = subprocess.Popen(server_data_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    server_data_output, _ = server_data_process.communicate()
    
    server_data_status = server_data_output.decode().strip()
    http_status = "✅ **HTTP Unblocked**" if server_data_status not in ["403", "404", "502"] else "❌ **HTTP Blocked**"

    return f"{gt_status}\n{http_status}"

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} siap!")

# Perintah iptosub (hanya Owner)
@bot.command()
async def iptosub(ctx, ip: str):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini!", ephemeral=True)

    subdomain = add_subdomain(ip)
    if subdomain:
        await ctx.send(f"✅ Subdomain berhasil dibuat: `{subdomain}`", ephemeral=True)
    else:
        await ctx.send("❌ Gagal membuat subdomain!", ephemeral=True)

# Perintah check proxy
@bot.command()
async def check(ctx, proxy: str):
    try:
        ip, port, username, password = proxy.split(":")
    except ValueError:
        return await ctx.send("❌ Format salah! Gunakan `/check ip:port:username:password`", ephemeral=True)

    await ctx.send("🔄 **Sedang memeriksa proxy...**", ephemeral=True)
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, check_proxy, ip, port, username, password)
    
    await ctx.send(result, ephemeral=True)

bot.run(TOKEN)
