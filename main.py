import asyncio
import math

import aiohttp
import discord
from pprint import pformat
from Classes.ServerResponseSingle import server_response_single_from_dict, ServerResponseSingle, server_response_single_to_dict
import json
from datetime import datetime
from os import path, environ
from os import stat as os_stat
from stat import ST_MTIME
from time import time

def modification_date(filename):
    t = path.getmtime(filename)
    return datetime.fromtimestamp(t)
def file_age_in_seconds(pathname):
    return time() - os_stat(pathname)[ST_MTIME]
def embed_not_empty(embed):
    return embed.title or embed.description or (embed.footer is not discord.Embed.Empty) or (embed.fields is not discord.Embed.Empty)
def cacheFile(id):
    return f"cache/{id}.cache.json"

class MyClient(discord.Client):
    api_url = "https://servers-frontend.fivem.net/api/servers/single/"
    servers = { "erp": "ykv8z5", "erp-test": "l8r6jj"} # vkj37r
    webclient: aiohttp.ClientSession
    channel: discord.TextChannel

    async def on_ready(self):
        self.webclient = aiohttp.ClientSession()
        self.webclient.timeout.total = 15
        print(f"[AIOHTTP] Client created. {self.webclient.timeout}")
        self.channel = self.get_channel(847469532174876683)
        print(f'[DISCORD] Logged on as {self.user} ({self.user.id})')
        # client.loop.create_task(self.main_loop())

    async def on_message(self, message: discord.Message):
        if message.content == "ping":
            await message.reply("pong")
        elif message.content.startswith("server "):
            await self.check_5mserver(message.content.split(" ")[-1])
        elif message.content == "servers":
            await self.main_loop(True)

    async def main_loop(self, destroy = False):
        print(f"Checking {len(self.servers)} servers...")
        while True:
            for name, sid in self.servers.items():
                print(f"Checking server \"{name}\" ({sid})")
                await self.check_5mserver(sid)
            if destroy: break
            await asyncio.sleep(120)

    async def check_5mserver(self, sid):
        cfile = cacheFile(sid)
        last_response: ServerResponseSingle
        if path.isfile(cfile):
            cache_age = file_age_in_seconds(cfile)
            if cache_age < 60:
                print(f"{cfile} too new ({math.floor(cache_age)}s)")
                return
            print(f"Using {cfile}")
            last_response = server_response_single_from_dict(self.load_response(cfile))
        else:
            last_response = ServerResponseSingle()
        url = self.api_url + sid
        print("[AIOHTTP] Requesting " + url)
        async with self.webclient.get(url) as response:
            print(pformat(response))
            print("Status:", response.status)
            if response.status != 200: return
            print("Content-type:", response.headers['content-type'])
            _json = await response.json()
            print(_json)
            try:
                fivem_server = server_response_single_from_dict(json)
                embed = discord.Embed()
                print(last_response.data.vars.sv_enforce_game_build)
                print("=>")
                print(fivem_server.data.vars.sv_enforce_game_build)
                if fivem_server.data.vars.sv_enforce_game_build != last_response.data.vars.sv_enforce_game_build:
                    embed.add_field("Game Version", f"```diff\n-{last_response.data.vars.sv_enforce_game_build}\n+{fivem_server.data.vars.sv_enforce_game_build}```", True)
                print(pformat(fivem_server))
                if embed_not_empty(embed):
                    embed.title = "Changes Detected!"
                    embed.colour = discord.Colour.orange
                    await self.channel.send(embed=embed)
            except Exception as ex: print(ex)
            self.save_response(_json, cfile)

    def load_response(self, filename):
        if not path.isfile(filename): self.save_response({}, filename)
        with open(filename, 'r', encoding='utf-8') as f:
            _json = json.load(f)
        return _json

    def save_response(self, _json, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(_json, f, ensure_ascii=False, indent=4)

client = MyClient()
client.run(environ['DISCORD_BOT_TOKEN'])
