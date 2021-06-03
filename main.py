import asyncio
import json
import os
import re
from datetime import datetime
from os import path
from os import stat as os_stat
from pprint import pformat, pprint
from stat import ST_MTIME
from time import time
from pathlib import Path
from typing import Optional, Any, List, TypeVar, Type, Callable, cast

import aiohttp
import discord

from Classes.Player import Player, PlayerDB
from Classes import Server
from Classes.fivem.ServerResponseSingle import server_response_single_from_dict, ServerResponseSingle


def modification_date(filename) -> datetime:
    t = path.getmtime(filename)
    return datetime.fromtimestamp(t)
def file_age_in_seconds(pathname) -> float:
    return time() - os_stat(pathname)[ST_MTIME]
def embed_not_empty(embed) -> bool:
    return embed.title or embed.description or (embed.footer is not discord.Embed.Empty) or (
                embed.fields is not discord.Embed.Empty)
def cacheFile(id) -> str:
    return f"cache/{id}.cache.json"
def sanitize(input) -> str:
    return re.sub(r"\^\d", "", input.strip(), 0, re.MULTILINE)


def getDiff(old, new) -> Optional[str]:
    missing = (set(old).difference(new))
    is_missing = len(missing) > 0
    added = (set(new).difference(old))
    is_added = len(added) > 0
    if is_missing or is_added:
        i = ["```diff"]
        if is_missing: i.append("- " + '\n- '.join(sorted(missing, key=str.lower)))
        if is_added:   i.append("+ " + '\n+ '.join(sorted(added, key=str.lower)))
        i.append("```")
        return '\n'.join(i)
    return None


def getPlayerDiff(old, new) -> Optional[str]:
    missing = (set(old).difference(new))
    is_missing = len(missing) > 0
    added = (set(new).difference(old))
    is_added = len(added) > 0
    if is_missing or is_added:
        i = ["```diff"]
        if is_missing: i.append("- " + '\n- '.join(getPlayers(missing)))
        if is_added:   i.append("+ " + '\n+ '.join(getPlayers(added)))
        i.append("```")
        return '\n'.join(i)
    return None


def getPlayers(players) -> List[str]:
    return sorted([f"#{o.id} \"{sanitize(o.name)}\" ({o.ping}ms)" for o in players])


class MyClient(discord.Client):
    api_url = "https://servers-frontend.fivem.net/api/servers/single/"
    servers: list
    webclient: aiohttp.ClientSession
    channel: discord.TextChannel
    min_cache_time = 15
    playersDBFile = "cache/players.db.json"
    playersDB: PlayerDB

    def __init__(self, **options):
        super().__init__(**options)
        self.servers = list()
        self.servers.append(Server.Server("ykv8z5", "EndlessRP", ""))
        self.servers.append(Server.Server("l8r6jj", "EndlessRP Test", "")) # vkj37r
        self.playersDB = PlayerDB(self.playersDBFile)

    async def on_ready(self):
        self.webclient = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        print(f"[AIOHTTP] Client created. {self.webclient.timeout}")
        self.channel = self.get_channel(847469532174876683)
        print(f'[DISCORD] Logged on as {self.user} ({self.user.id})')
        client.loop.create_task(self.main_loop())

    async def on_message(self, message: discord.Message):
        cmd = message.content.split(" ")
        sid = "ykv8z5"
        if len(cmd) == 2: sid = cmd[1]
        if cmd[0] == "!ping":
            await message.reply("pong")
        elif cmd[0] == "!server":
            await self.check_5mserver(sid)
        elif cmd[0] == "!servers":
            pprint(self.servers)
            await self.channel.send(pformat(self.servers))
            await self.main_loop(True)
        elif cmd[0] == "!players":
            cache = self.get_Cache(cacheFile(sid))
            if not cache: cache = await self.get_Server(sid)
            embed = discord.Embed()
            embed.colour = discord.Colour.green()
            embed.title = f"Players [{len(cache.data.players)} / {cache.data.sv_maxclients}]"
            for player in cache.data.players:
                embed.add_field(name=f"{player.name} (#{player.id})", value=f"{player.ping}ms")
            await self.send_message(cache, embed=embed)
        elif cmd[0] == "!player" and len(cmd) > 1:
            name = " ".join(cmd.pop(0))
            await self.channel.send(content="```json\n"+json.dumps(Player.to_dict(self.playersDB.getByName(name)[0]))+"\n```")
        elif cmd[0] == "!resources":
            cache = self.get_Cache(cacheFile(sid))
            if not cache: cache = await self.get_Server(sid)
            await self.send_message(cache, message="```css\n"+(sanitize(",".join(cache.data.resources))+"\n```"))

    async def main_loop(self, destroy = False):
        print(f"Checking {len(self.servers)} servers...")
        while True:
            for s in self.servers:
                print(f"Checking server \"{s.name}\" ({s.id})")
                await self.check_5mserver(s)
                await asyncio.sleep(15)
            if destroy: break
            await asyncio.sleep(120)

    async def send_message(self, server:ServerResponseSingle, message:str = None, embed:discord.Embed = None):
        if not embed: embed = discord.Embed()
        embed.set_footer(text=sanitize(server.data.vars.sv_project_name))
        if not embed.timestamp: embed.timestamp = datetime.now()
        embed.colour = discord.Colour.orange()
        print(pformat(embed))
        await self.channel.send(content=message, embed=embed)

    def get_Cache(self, cfile:str):
        if path.isfile(cfile):
            """
            cache_age = file_age_in_seconds(cfile)
            if cache_age < self.min_cache_time:
                print(f"{cfile} too new ({math.floor(cache_age)}s / {self.min_cache_time}s)")
                return
            """
            print(f"Using {cfile}")
            return server_response_single_from_dict(self.load_response(cfile))
        else:
            Path("cache/").mkdir(parents=True, exist_ok=True)
            return None

    async def get_Server(self, sid):
        cfile = cacheFile(sid)
        url = self.api_url + sid
        async with self.webclient.get(url) as response:
            _json = await response.json()
            print(_json)
            self.save_response(_json, cfile)
            return server_response_single_from_dict(_json)

    async def check_5mserver(self, server):
        try:
            cfile = cacheFile(server.id)
            last_response = self.get_Cache(cfile)
            url = self.api_url + server.id
            print("[AIOHTTP] Requesting " + url)
            now = datetime.now()
            async with self.webclient.get(url) as response:
                print(pformat(response))
                if response.status != 200:
                    await self.fail(server, f"```\n[{now}]Failed to request data for \"{server.name}\" ({server.id}): HTTP ERROR {response.status}\n```", now)
                    return
                _json = await response.json()
                print(_json)
                self.save_response(_json, cfile)
                if last_response is None: return
                fivem_server = server_response_single_from_dict(_json)
                print(pformat(fivem_server))
                server.error = ""
                embed = discord.Embed()
                changes = []
                # CHANGES START
                if fivem_server.data.resources != last_response.data.resources:
                    embed.add_field(name="Resources",
                                    value=getDiff(last_response.data.resources, fivem_server.data.resources).replace("%20", " "))
                    changes.append("resources")
                if fivem_server.data.vars.sv_enforce_game_build != last_response.data.vars.sv_enforce_game_build:
                    embed.add_field(name="Game Version",
                                    value=f"```diff\n-{last_response.data.vars.sv_enforce_game_build}\n+{fivem_server.data.vars.sv_enforce_game_build}```")
                    changes.append("game version")
                if fivem_server.data.players != last_response.data.players:
                    embed.add_field(name="Players",
                                    value=getPlayerDiff(last_response.data.players, fivem_server.data.players),
                                    inline=False)
                    changes.append("players")
                # CHANGES END
                if changes:
                    embed.title = "Changes Detected!"
                    embed.description = f"fivem://connect/{server.id}"
                    embed.url = f"https://servers.fivem.net/servers/detail/{server.id}"
                    embed.colour = discord.Colour.orange()
                    embed.timestamp = now
                    await self.send_message(fivem_server, message="**Changes**: " + ", ".join(changes), embed=embed)
                try:
                    for player in fivem_server.data.players:
                        self.playersDB.updatePlayer(fivem_server, player)
                    self.playersDB.save()
                except Exception as ex:
                    await self.fail(server, f"```\nFailed to index players for \"{server.name}\" ({server.id}): {str(ex)}\n``` <@467777925790564352>", now)
                await self.channel.edit(topic=f"[{len(fivem_server.data.players)} / {fivem_server.data.sv_maxclients}] {sanitize(fivem_server.data.vars.sv_project_name)}\nLast Updated: {now}")
        except Exception as ex:
            await self.fail(server, f"```\nFailed to request data for \"{server.name}\" ({server.id}): {ex.args}\n``` <@467777925790564352>", now)

    def load_response(self, filename):
        if not path.isfile(filename): self.save_response({}, filename)
        with open(filename, 'r', encoding='utf-8') as f:
            _json = json.load(f)
        return _json

    def save_response(self, _json, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(_json, f, ensure_ascii=False, indent=4)

    def serverById(self, id):
        return next(s for s in self.servers if s.id == id)

    async def fail(self, server, error, timestamp):
        pprint(error)
        if server.error == error: return
        server.error = error
        await self.channel.send(f"[{timestamp}] {error}")

client = MyClient()
client.run(os.environ["DISCORD_BOT_TOKEN"])
