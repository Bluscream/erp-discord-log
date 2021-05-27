import asyncio
import json
import math
import re
from datetime import datetime
from os import path, environ
from os import stat as os_stat
from pprint import pformat
from stat import ST_MTIME
from time import time

import aiohttp
import discord

from Classes.ServerResponseSingle import server_response_single_from_dict, ServerResponseSingle


def modification_date(filename):
    t = path.getmtime(filename)
    return datetime.fromtimestamp(t)


def file_age_in_seconds(pathname):
    return time() - os_stat(pathname)[ST_MTIME]


def embed_not_empty(embed):
    return embed.title or embed.description or (embed.footer is not discord.Embed.Empty) or (
                embed.fields is not discord.Embed.Empty)


def cacheFile(id):
    return f"cache/{id}.cache.json"


def sanitize(input):
    return re.sub(r"\^\d", "", input.strip(), 0, re.MULTILINE)


def getDiffText(old, new):
    missing = (set(old).difference(new));
    is_missing = len(missing) > 0
    added = (set(new).difference(old));
    is_added = len(added) > 0
    if is_missing or is_added:
        i = ["```diff"]
        if is_missing: i.append("- " + '\n- '.join(missing))
        if is_added:   i.append("+ " + '\n+ '.join(added))
        i.append("```")
        return '\n'.join(i)
    return None


def getPlayers(players):
    return [f"#{o.id} \"{sanitize(o.name)}\" ({o.ping}ms)" for o in players]


class MyClient(discord.Client):
    api_url = "https://servers-frontend.fivem.net/api/servers/single/"
    servers = {"ykv8z5": "erp", "l8r6jj": "erp-test"}
    webclient: aiohttp.ClientSession
    channel: discord.TextChannel
    min_cache_time = 15

    async def on_ready(self):
        self.webclient = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
        print(f"[AIOHTTP] Client created. {self.webclient.timeout}")
        self.channel = self.get_channel(847469532174876683)
        print(f'[DISCORD] Logged on as {self.user} ({self.user.id})')
        client.loop.create_task(self.main_loop())

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
            for sid, name in self.servers.items():
                print(f"Checking server \"{name}\" ({sid})")
                await self.check_5mserver(sid)
                await asyncio.sleep(15)
            if destroy: break
            await asyncio.sleep(120)

    async def check_5mserver(self, sid):
        try:
            cfile = cacheFile(sid)
            last_response: ServerResponseSingle
            if path.isfile(cfile):
                cache_age = file_age_in_seconds(cfile)
                if cache_age < self.min_cache_time:
                    print(f"{cfile} too new ({math.floor(cache_age)}s / {self.min_cache_time}s)")
                    return
                print(f"Using {cfile}")
                last_response = server_response_single_from_dict(self.load_response(cfile))
            else:
                last_response = ServerResponseSingle()
            url = self.api_url + sid
            print("[AIOHTTP] Requesting " + url)
            now = datetime.now()
            async with self.webclient.get(url) as response:
                print(pformat(response))
                if response.status != 200:
                    await self.channel.send(
                        f"```\nFailed to request data for \"{self.servers[sid]}\" ({sid}): HTTP ERROR {response.status}\n```")
                    return
                _json = await response.json()
                print(_json)
                fivem_server = server_response_single_from_dict(_json)
                print(pformat(fivem_server))
                embed = discord.Embed();
                changes = 0
                # CHANGES START
                if fivem_server.data.resources != last_response.data.resources:
                    embed.add_field(name="Resources",
                                    value=getDiffText(last_response.data.resources, fivem_server.data.resources));
                    changes += 1
                if fivem_server.data.vars.sv_enforce_game_build != last_response.data.vars.sv_enforce_game_build:
                    embed.add_field(name="Game Version",
                                    value=f"```diff\n-{last_response.data.vars.sv_enforce_game_build}\n+{fivem_server.data.vars.sv_enforce_game_build}```");
                    changes += 1
                if fivem_server.data.players != last_response.data.players:
                    embed.add_field(name="Players", value=getDiffText(getPlayers(last_response.data.players),
                                                                      getPlayers(fivem_server.data.players)),
                                    inline=False);
                    changes += 1
                # CHANGES END
                if changes:
                    embed.title = "Changes Detected!"
                    embed.description = f"fivem://connect/{sid}"
                    embed.url = f"https://servers.fivem.net/servers/detail/{sid}"
                    embed.set_footer(text=sanitize(fivem_server.data.hostname))
                    embed.timestamp = now
                    embed.colour = discord.Colour.orange()
                    print(pformat(embed))
                    await self.channel.send(embed=embed)
                #
                self.save_response(_json, cfile)
        except Exception as ex:
            print(f"{ex}")
            await self.channel.send(
                f"```\nFailed to request data for \"{self.servers[sid]}\" ({sid}): {ex.args[0]}\n```")

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
