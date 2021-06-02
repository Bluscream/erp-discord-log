# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = server_response_single_from_dict(json.loads(json_string))

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, TypeVar, Callable, Type, cast
from uuid import UUID

import dateutil.parser

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_stringified_bool(x: str) -> bool:
    if x == "true":
        return True
    if x == "false":
        return False
    assert False


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Player:
    endpoint: Optional[str] = None
    id: Optional[int] = None
    identifiers: Optional[List[str]] = None
    name: Optional[str] = None
    ping: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        assert isinstance(obj, dict)
        endpoint = from_union([from_str, from_none], obj.get("endpoint"))
        id = from_union([from_int, from_none], obj.get("id"))
        identifiers = from_union([lambda x: from_list(from_str, x), from_none], obj.get("identifiers"))
        name = from_union([from_str, from_none], obj.get("name"))
        ping = from_union([from_int, from_none], obj.get("ping"))
        return Player(endpoint, id, identifiers, name, ping)

    def to_dict(self) -> dict:
        result: dict = {}
        result["endpoint"] = from_union([lambda x: to_enum(Endpoint, x), from_none], self.endpoint)
        result["id"] = from_union([from_int, from_none], self.id)
        result["identifiers"] = from_union([lambda x: from_list(from_str, x), from_none], self.identifiers)
        result["name"] = from_union([from_str, from_none], self.name)
        result["ping"] = from_union([from_int, from_none], self.ping)
        return result

    def __str__(self):
        return f"\"{self.name}\" (#{self.id})"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name

@dataclass
class Vars:
    onesync_enabled: Optional[bool] = None
    sv_enforce_game_build: Optional[int] = None
    sv_enhanced_host_support: Optional[bool] = None
    sv_lan: Optional[bool] = None
    sv_max_clients: Optional[int] = None
    sv_script_hook_allowed: Optional[bool] = None
    essential_mode_uuid: Optional[UUID] = None
    essential_mode_version: Optional[str] = None
    routen: Optional[str] = None
    banner_connecting: Optional[str] = None
    banner_detail: Optional[str] = None
    gamename: Optional[str] = None
    locale: Optional[str] = None
    sv_license_key_token: Optional[str] = None
    sv_project_desc: Optional[str] = None
    sv_project_name: Optional[str] = None
    tags: Optional[str] = None
    tx_admin_version: Optional[str] = None
    discord: Optional[str] = None
    teamspeak: Optional[str] = None
    roleplay: Optional[str] = None
    premium: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Vars':
        assert isinstance(obj, dict)
        onesync_enabled = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("onesync_enabled"))
        sv_enforce_game_build = from_union([from_none, lambda x: int(from_str(x))], obj.get("sv_enforceGameBuild"))
        sv_enhanced_host_support = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("sv_enhancedHostSupport"))
        sv_lan = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("sv_lan"))
        sv_max_clients = from_union([from_none, lambda x: int(from_str(x))], obj.get("sv_maxClients"))
        sv_script_hook_allowed = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("sv_scriptHookAllowed"))
        essential_mode_uuid = from_union([lambda x: UUID(x), from_none], obj.get("EssentialModeUUID"))
        essential_mode_version = from_union([from_str, from_none], obj.get("EssentialModeVersion"))
        routen = from_union([from_str, from_none], obj.get("Routen"))
        banner_connecting = from_union([from_str, from_none], obj.get("banner_connecting"))
        banner_detail = from_union([from_str, from_none], obj.get("banner_detail"))
        gamename = from_union([from_str, from_none], obj.get("gamename"))
        locale = from_union([from_str, from_none], obj.get("locale"))
        sv_license_key_token = from_union([from_str, from_none], obj.get("sv_licenseKeyToken"))
        sv_project_desc = from_union([from_str, from_none], obj.get("sv_projectDesc"))
        sv_project_name = from_union([from_str, from_none], obj.get("sv_projectName"))
        tags = from_union([from_str, from_none], obj.get("tags"))
        tx_admin_version = from_union([from_str, from_none], obj.get("txAdmin-version"))
        discord = from_union([from_str, from_none], obj.get("\U0001f4dd Discord"))
        teamspeak = from_union([from_str, from_none], obj.get("\U0001f50a Teamspeak"))
        roleplay = from_union([from_str, from_none], obj.get("\U0001f525 Roleplay "))
        premium = from_union([from_str, from_none], obj.get("premium"))
        return Vars(onesync_enabled, sv_enforce_game_build, sv_enhanced_host_support, sv_lan, sv_max_clients, sv_script_hook_allowed, essential_mode_uuid, essential_mode_version, routen, banner_connecting, banner_detail, gamename, locale, sv_license_key_token, sv_project_desc, sv_project_name, tags, tx_admin_version, discord, teamspeak, roleplay, premium)

    def to_dict(self) -> dict:
        result: dict = {}
        result["onesync_enabled"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.onesync_enabled)
        result["sv_enforceGameBuild"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.sv_enforce_game_build)
        result["sv_enhancedHostSupport"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.sv_enhanced_host_support)
        result["sv_lan"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.sv_lan)
        result["sv_maxClients"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.sv_max_clients)
        result["sv_scriptHookAllowed"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.sv_script_hook_allowed)
        result["EssentialModeUUID"] = from_union([lambda x: str(x), from_none], self.essential_mode_uuid)
        result["EssentialModeVersion"] = from_union([from_str, from_none], self.essential_mode_version)
        result["Routen"] = from_union([from_str, from_none], self.routen)
        result["banner_connecting"] = from_union([from_str, from_none], self.banner_connecting)
        result["banner_detail"] = from_union([from_str, from_none], self.banner_detail)
        result["gamename"] = from_union([from_str, from_none], self.gamename)
        result["locale"] = from_union([from_str, from_none], self.locale)
        result["sv_licenseKeyToken"] = from_union([from_str, from_none], self.sv_license_key_token)
        result["sv_projectDesc"] = from_union([from_str, from_none], self.sv_project_desc)
        result["sv_projectName"] = from_union([from_str, from_none], self.sv_project_name)
        result["tags"] = from_union([from_str, from_none], self.tags)
        result["txAdmin-version"] = from_union([from_str, from_none], self.tx_admin_version)
        result["\U0001f4dd Discord"] = from_union([from_str, from_none], self.discord)
        result["\U0001f50a Teamspeak"] = from_union([from_str, from_none], self.teamspeak)
        result["\U0001f525 Roleplay "] = from_union([from_str, from_none], self.roleplay)
        result["premium"] = from_union([from_str, from_none], self.premium)
        return result


@dataclass
class Data:
    clients: Optional[int] = None
    gametype: Optional[str] = None
    hostname: Optional[str] = None
    mapname: Optional[str] = None
    data_sv_maxclients: Optional[int] = None
    enhanced_host_support: Optional[bool] = None
    resources: Optional[List[str]] = None
    server: Optional[str] = None
    vars: Optional[Vars] = None
    self_reported_clients: Optional[int] = None
    players: Optional[List[Player]] = None
    owner_id: Optional[int] = None
    connect_end_points: Optional[List[str]] = None
    upvote_power: Optional[int] = None
    support_status: Optional[str] = None
    sv_maxclients: Optional[int] = None
    owner_name: Optional[str] = None
    owner_profile: Optional[str] = None
    owner_avatar: Optional[str] = None
    last_seen: Optional[datetime] = None
    icon_version: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        assert isinstance(obj, dict)
        clients = from_union([from_int, from_none], obj.get("clients"))
        gametype = from_union([from_str, from_none], obj.get("gametype"))
        hostname = from_union([from_str, from_none], obj.get("hostname"))
        mapname = from_union([from_str, from_none], obj.get("mapname"))
        data_sv_maxclients = from_union([from_int, from_none], obj.get("sv_maxclients"))
        enhanced_host_support = from_union([from_bool, from_none], obj.get("enhancedHostSupport"))
        resources = from_union([lambda x: from_list(from_str, x), from_none], obj.get("resources"))
        server = from_union([from_str, from_none], obj.get("server"))
        vars = from_union([Vars.from_dict, from_none], obj.get("vars"))
        self_reported_clients = from_union([from_int, from_none], obj.get("selfReportedClients"))
        players = from_union([lambda x: from_list(Player.from_dict, x), from_none], obj.get("players"))
        owner_id = from_union([from_int, from_none], obj.get("ownerID"))
        connect_end_points = from_union([lambda x: from_list(from_str, x), from_none], obj.get("connectEndPoints"))
        upvote_power = from_union([from_int, from_none], obj.get("upvotePower"))
        support_status = from_union([from_str, from_none], obj.get("support_status"))
        sv_maxclients = from_union([from_int, from_none], obj.get("svMaxclients"))
        owner_name = from_union([from_str, from_none], obj.get("ownerName"))
        owner_profile = from_union([from_str, from_none], obj.get("ownerProfile"))
        owner_avatar = from_union([from_str, from_none], obj.get("ownerAvatar"))
        last_seen = from_union([from_datetime, from_none], obj.get("lastSeen"))
        icon_version = from_union([from_int, from_none], obj.get("iconVersion"))
        return Data(clients, gametype, hostname, mapname, data_sv_maxclients, enhanced_host_support, resources, server, vars, self_reported_clients, players, owner_id, connect_end_points, upvote_power, support_status, sv_maxclients, owner_name, owner_profile, owner_avatar, last_seen, icon_version)

    def to_dict(self) -> dict:
        result: dict = {}
        result["clients"] = from_union([from_int, from_none], self.clients)
        result["gametype"] = from_union([from_str, from_none], self.gametype)
        result["hostname"] = from_union([from_str, from_none], self.hostname)
        result["mapname"] = from_union([from_str, from_none], self.mapname)
        result["sv_maxclients"] = from_union([from_int, from_none], self.data_sv_maxclients)
        result["enhancedHostSupport"] = from_union([from_bool, from_none], self.enhanced_host_support)
        result["resources"] = from_union([lambda x: from_list(from_str, x), from_none], self.resources)
        result["server"] = from_union([from_str, from_none], self.server)
        result["vars"] = from_union([lambda x: to_class(Vars, x), from_none], self.vars)
        result["selfReportedClients"] = from_union([from_int, from_none], self.self_reported_clients)
        result["players"] = from_union([lambda x: from_list(lambda x: to_class(Player, x), x), from_none], self.players)
        result["ownerID"] = from_union([from_int, from_none], self.owner_id)
        result["connectEndPoints"] = from_union([lambda x: from_list(from_str, x), from_none], self.connect_end_points)
        result["upvotePower"] = from_union([from_int, from_none], self.upvote_power)
        result["support_status"] = from_union([from_str, from_none], self.support_status)
        result["svMaxclients"] = from_union([from_int, from_none], self.sv_maxclients)
        result["ownerName"] = from_union([from_str, from_none], self.owner_name)
        result["ownerProfile"] = from_union([from_str, from_none], self.owner_profile)
        result["ownerAvatar"] = from_union([from_str, from_none], self.owner_avatar)
        result["lastSeen"] = from_union([lambda x: x.isoformat(), from_none], self.last_seen)
        result["iconVersion"] = from_union([from_int, from_none], self.icon_version)
        return result


@dataclass
class ServerResponseSingle:
    end_point: Optional[str] = None
    data: Optional[Data] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ServerResponseSingle':
        assert isinstance(obj, dict)
        end_point = from_union([from_str, from_none], obj.get("EndPoint"))
        data = from_union([Data.from_dict, from_none], obj.get("Data"))
        return ServerResponseSingle(end_point, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["EndPoint"] = from_union([from_str, from_none], self.end_point)
        result["Data"] = from_union([lambda x: to_class(Data, x), from_none], self.data)
        return result


def server_response_single_from_dict(s: Any) -> ServerResponseSingle:
    return ServerResponseSingle.from_dict(s)


def server_response_single_to_dict(x: ServerResponseSingle) -> Any:
    return to_class(ServerResponseSingle, x)
