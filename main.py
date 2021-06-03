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
from Classes.Server import Server
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


def sanitize(input: str) -> str:
    # log(f"Sanitizing {input}", False, True)
    return re.sub(r"\^\d", "", input.strip(), 0, re.MULTILINE)


def cut(input: str) -> str:
    if input is None: return input
    return input[:2000]


def log(message, pretty=False, debug=False):
    if debug: return
    if message is str and pretty: message = pformat(message)
    print(f"[{datetime.now()}] {message}")


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
    servers: List[Server]
    webclient: aiohttp.ClientSession
    min_cache_time = 15
    playersDBFile = "cache/players.db.json"
    playersDB: PlayerDB

    def __init__(self, **options):
        super().__init__(**options)
        self.servers = list()
        self.servers.append(Server("ykv8z5", "EndlessRP", "", 847469532174876683))
        self.servers.append(Server("l8r6jj", "EndlessRP Test", "", 849809046453485618))
        self.servers.append(Server("vkj37r", "Drift Fantasy", "", 849812243042533376, True))
        self.playersDB = PlayerDB(self.playersDBFile)

    async def on_ready(self):
        self.webclient = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        log(f"[AIOHTTP] Client created. {self.webclient.timeout}")
        log(f'[DISCORD] Logged on as {self.user} ({self.user.id})')
        for server in self.servers:
            server.channel = self.get_channel(server.channel)
        client.loop.create_task(self.main_loop())

    async def on_message(self, message: discord.Message):
        cmd = message.content.split(" ")
        server = self.servers[0]
        for _server in self.servers:
            if _server.channel.id == message.channel.id:
                server = _server
        if len(cmd) == 2: server = Server(cmd[1], f"manual input ({cmd[1]})", "", message.channel)
        if cmd[0] == "!ping":
            await self.reply(message, "pong")
        elif cmd[0] == "!server":
            await self.check_5mserver(server)
        elif cmd[0] == "!toggle":
            server.disabled = not server.disabled
            status = "disabled" if server.disabled else "enabled"
            await self.reply(message, content=f"{server.name} is now {status}")
        elif cmd[0] == "!servers":
            # log(self.servers, True, True)
            await self.servers[0].channel.send(pformat(self.servers))
            await self.main_loop(True)
        elif cmd[0] == "!players":
            cache = self.get_Cache(cacheFile(server.id))
            if not cache: cache = await self.get_Server(server.id)
            embed = discord.Embed()
            embed.colour = discord.Colour.green()
            embed.title = f"Players [{len(cache.data.players)} / {cache.data.sv_maxclients}]"
            for player in cache.data.players:
                embed.add_field(name=f"{player.name} (#{player.id})", value=f"{player.ping}ms")
            await self.reply(message, embed=embed)
        elif cmd[0] == "!player" and len(cmd) > 1:
            name = " ".join(cmd.pop(0))
            await self.reply(message, content="```json\n" + json.dumps(
                Player.to_dict(self.playersDB.getByName(name)[0])) + "\n```")
        elif cmd[0] == "!resources":
            cache = self.get_Cache(cacheFile(server.id))
            if not cache: cache = await self.get_Server(server.id)
            await self.reply(message, content="```css\n" + (sanitize(",".join(cache.data.resources)) + "\n```"))

    async def main_loop(self, destroy=False):
        log(f"Checking {len(self.servers)} servers...")
        while True:
            for s in self.servers:
                if s.disabled:
                    log(f"Server \"{s.name}\" ({s.id}) is disabled, skipping...")
                    continue
                log("Waiting 5 seconds for next server ...")
                await asyncio.sleep(5)
                log(f"Checking server \"{s.name}\" ({s.id})")
                await self.check_5mserver(s)
            if destroy: break
            log("Waiting 55 seconds for next round ...")
            await asyncio.sleep(55)

    async def send_message(self, _server: Server, server: ServerResponseSingle, message: str = None,
                           embed: discord.Embed = None):
        if not embed: embed = discord.Embed()
        if not embed.footer: embed.set_footer(text=sanitize(server.data.hostname))
        if not embed.timestamp: embed.timestamp = datetime.now()
        if not embed.color: embed.colour = discord.Colour.orange()
        log(embed, pretty=True, debug=True)
        if message: message += " ||<@&849813983434113076>||"
        await _server.channel.send(content=cut(message), embed=embed)

    async def reply(self, original_message: discord.Message, content: str = None, embed: discord.Embed = None):
        await original_message.reply(content=cut(content), embed=embed)

    def get_Cache(self, cfile: str):
        if path.isfile(cfile):
            """
            cache_age = file_age_in_seconds(cfile)
            if cache_age < self.min_cache_time:
                log(f"{cfile} too new ({math.floor(cache_age)}s / {self.min_cache_time}s)")
                return
            """
            log(f"Using {cfile}")
            return server_response_single_from_dict(self.load_response(cfile))
        else:
            Path("cache/").mkdir(parents=True, exist_ok=True)
            return None

    async def get_Server(self, sid):
        cfile = cacheFile(sid)
        url = self.api_url + sid
        async with self.webclient.get(url) as response:
            _json = await response.json()
            log(_json, debug=True)
            self.save_response(_json, cfile)
            return server_response_single_from_dict(_json)

    async def check_5mserver(self, server):
        try:
            cfile = cacheFile(server.id)
            last_response = self.get_Cache(cfile)
            url = self.api_url + server.id
            log("[AIOHTTP] Requesting " + url)
            now = datetime.now()
            async with self.webclient.get(url) as response:
                log(response, pretty=True, debug=True)
                if response.status != 200:
                    await self.fail(server,
                                    f"Failed to request data for \"{server.name}\" ({server.id}): HTTP ERROR {response.status}",
                                    now)
                    return
                _json = await response.json()
                log(_json, pretty=False, debug=True)
                self.save_response(_json, cfile)
                if last_response is None: return
                fivem_server = server_response_single_from_dict(_json)
                log(fivem_server, pretty=True, debug=True)
                server.error = ""
                embed = discord.Embed()
                changes = []
                # CHANGES START
                if fivem_server.data.resources != last_response.data.resources:
                    embed.add_field(name="Resources",
                                    value=getDiff(last_response.data.resources, fivem_server.data.resources).replace(
                                        "%20", " "))
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
                    await self.send_message(server, fivem_server, message="**Changes**: " + ", ".join(changes),
                                            embed=embed)
                    for player in fivem_server.data.players:
                        try:
                            self.playersDB.updatePlayer(fivem_server, player)
                        except Exception as ex:
                            pass  # await self.fail(server, f"Failed to index players for \"{server.name}\" ({server.id}): {str(ex)}", now)
                    self.playersDB.save()
                asyncio.get_event_loop().create_task(self.update_topic(server, fivem_server, now))



        except Exception as ex:
            await self.fail(server, f"Failed to request data for \"{server.name}\" ({server.id}): {ex.args}", now)

    async def update_topic(self, server: Server, _server: ServerResponseSingle, timestamp):
        newtopic = f"[{len(_server.data.players)} / {_server.data.sv_maxclients}] {sanitize(_server.data.hostname)}"
        if server.channel.topic is None or not server.channel.topic.startswith(newtopic):
            log(f"Settings channel topic of {server.channel.name} to \"{newtopic}\"", False, False)
            await server.channel.edit(topic=newtopic+f"\nLast Updated: {timestamp}")

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

    async def fail(self, server, error, timestamp, notify=False):
        log(error, True)
        if server.error == error: return
        server.error = error
        await server.channel.send(
            content=cut(f"```\n[{timestamp}] {error}\n```" + (" ||<@467777925790564352>||" if notify else "")))


client = MyClient()
client.run(os.environ["DISCORD_BOT_TOKEN"])
