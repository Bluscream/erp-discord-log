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
#     result = player_from_dict(json.loads(json_string))

from dataclasses import dataclass
from pprint import pprint
from typing import Optional, Any, List, TypeVar, Type, Callable, cast
from datetime import datetime
import dateutil.parser


from os import path
import json
from Classes.fivem.ServerResponseSingle import Player as ServerPlayer
from Classes.fivem.ServerResponseSingle import ServerResponseSingle

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    # assert False


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Character:
    name: Optional[str] = None
    phone: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Character':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        phone = from_union([from_str, from_none], obj.get("phone"))
        return Character(name, phone)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_str, from_none], self.name)
        result["phone"] = from_union([from_str, from_none], self.phone)
        return result


@dataclass
class Endpoint:
    endpoint: Optional[str] = None
    last_seen: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Endpoint':
        assert isinstance(obj, dict)
        endpoint = from_union([from_str, from_none], obj.get("endpoint"))
        last_seen = from_union([from_datetime, from_none], obj.get("last_seen"))
        return Endpoint(endpoint, last_seen)

    def to_dict(self) -> dict:
        result: dict = {}
        result["endpoint"] = from_union([from_str, from_none], self.endpoint)
        result["last_seen"] = from_union([lambda x: x.isoformat(), from_none], self.last_seen)
        return result


@dataclass
class Identifier:
    identifier: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    last_seen: Optional[datetime] = None

    @staticmethod
    def from_str(identifier: str) -> 'Identifier':
        assert isinstance(identifier, str)
        split = identifier.split(":")
        name = split[0] if len(split) > 1 else ""
        value = split[1] if len(split) > 1 else ""
        return Identifier(identifier, name, value)

    @staticmethod
    def from_dict(obj: Any) -> 'Identifier':
        assert isinstance(obj, dict)
        identifier = from_union([from_str, from_none], obj.get("identifier"))
        split = identifier.split(":")
        name = split[0] if len(split) > 1 else ""
        value = split[1] if len(split) > 1 else ""
        last_seen = from_union([from_datetime, from_none], obj.get("last_seen"))
        return Identifier(identifier, name, value, last_seen)

    def to_dict(self) -> dict:
        result: dict = {}
        result["identifier"] = from_union([from_str, from_none], self.identifier)
        result["last_seen"] = from_union([lambda x: x.isoformat(), from_none], self.last_seen)
        return result


@dataclass
class Name:
    name: Optional[str] = None
    last_seen: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Name':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        last_seen = from_union([from_datetime, from_none], obj.get("last_seen"))
        return Name(name, last_seen)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_str, from_none], self.name)
        result["last_seen"] = from_union([lambda x: x.isoformat(), from_none], self.last_seen)
        return result


@dataclass
class Server:
    id: Optional[int] = None
    name: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Server':
        assert isinstance(obj, dict)
        id = from_union([from_none, lambda x: int(from_str(x))], obj.get("id"))
        name = from_union([from_none, lambda x: int(from_str(x))], obj.get("name"))
        return Server(id, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                   lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.id)
        result["name"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                     lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.name)
        return result


@dataclass
class SeenOn:
    server: Optional[Server] = None
    last_seen: Optional[datetime] = None
    characters: Optional[List[Character]] = None
    identifiers: Optional[List[Identifier]] = None
    endpoints: Optional[List[Endpoint]] = None
    names: Optional[List[Name]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SeenOn':
        assert isinstance(obj, dict)
        server = from_union([Server.from_dict, from_none], obj.get("server"))
        last_seen = from_union([from_datetime, from_none], obj.get("last_seen"))
        characters = from_union([lambda x: from_list(Character.from_dict, x), from_none], obj.get("characters"))
        identifiers = from_union([lambda x: from_list(Identifier.from_dict, x), from_none], obj.get("identifiers"))
        endpoints = from_union([lambda x: from_list(Endpoint.from_dict, x), from_none], obj.get("endpoints"))
        names = from_union([lambda x: from_list(Name.from_dict, x), from_none], obj.get("names"))
        return SeenOn(server, last_seen, characters, identifiers, endpoints, names)

    def to_dict(self) -> dict:
        result: dict = {}
        result["server"] = from_union([lambda x: to_class(Server, x), from_none], self.server)
        result["last_seen"] = from_union([lambda x: x.isoformat(), from_none], self.last_seen)
        result["characters"] = from_union([lambda x: from_list(lambda x: to_class(Character, x), x), from_none],
                                          self.characters)
        result["identifiers"] = from_union([lambda x: from_list(lambda x: to_class(Identifier, x), x), from_none],
                                           self.identifiers)
        result["endpoints"] = from_union([lambda x: from_list(lambda x: to_class(Endpoint, x), x), from_none],
                                         self.endpoints)
        result["names"] = from_union([lambda x: from_list(lambda x: to_class(Name, x), x), from_none], self.names)
        return result

    def update_name(self, name: str, time: datetime):
        for _name in self.names:
            if _name.name == name:
                name.last_seen = time
                return
        self.names.append(Name(name, time))


@dataclass
class Player:
    seen_on: Optional[List[SeenOn]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        assert isinstance(obj, dict)
        seen_on = from_union([lambda x: from_list(SeenOn.from_dict, x), from_none], obj.get("seen_on"))
        return Player(seen_on)

    @staticmethod
    def from_ServerPlayer(server: ServerResponseSingle, player: ServerPlayer):
        now = datetime.now()
        _seen_on = SeenOn()
        _seen_on.server = Server(server.end_point, server.data.hostname)
        _seen_on.last_seen = now
        _seen_on.characters = list()
        _seen_on.identifiers = list()
        for _id in player.identifiers:
            identifier = Identifier.from_str(_id)
            identifier.last_seen = now
            _seen_on.identifiers.append(identifier)
        _seen_on.endpoints = list()
        _seen_on.endpoints.append(Endpoint(player.endpoint, now))
        _seen_on.names = list()
        _seen_on.names.append(Name(player.name, now))
        _player = Player()
        _player.seen_on = list()
        _player.seen_on.append(_seen_on)
        pprint(_player)
        return _player

    def seenOnById(self, sid: str) -> SeenOn:
        for seen_on in self.seen_on:
            if seen_on.server.id == sid: return seen_on

    def to_dict(self) -> dict:
        result: dict = {}
        result["seen_on"] = from_union([lambda x: from_list(lambda x: to_class(SeenOn, x), x), from_none], self.seen_on)
        return result


def player_from_dict(s: Any) -> Player:
    return Player.from_dict(s)


def player_to_dict(x: Player) -> Any:
    return to_class(Player, x)

@dataclass
class PlayerDB:
    file: str
    players: List[Player]

    def __init__(self, file) -> None:
        self.players = list()
        self.load(file)

    def load(self, file) -> None:
        self.file = file
        if not path.isfile(file) or path.getsize(file) < 1:
            self.players = list()
            return
        with open(file, 'r', encoding='utf-8') as f:
            for player in json.load(f):
                self.players.append(player_from_dict(player))
        print(f"Loaded PlayerDB from \"{file}\" with {len(self.players)} players.")

    def save(self) -> None:
        with open(self.file, 'w', encoding='utf-8') as f:
            lst = list()
            for player in self.players:
                lst.append(player_to_dict(player))
            json.dump(lst, f, ensure_ascii=False, indent=4)
        print(f"Saved PlayerDB to \"{self.file}\" with {len(self.players)} players.")

    def getByName(self, name: str) -> List[Player]:
        result = list()
        for player in self.players:
            for server in player.seen_on:
                for _name in server.names:
                    if name == _name: result.append(player)
        return result

    def getByIdentifier(self, name: str, id: str) -> List[Player]:
        result = list()
        for player in self.players:
            for server in player.seen_on:
                for identifier in server.identifiers:
                    if identifier.value == id and identifier.name == name: result.append(player)
        return result

    def updatePlayer(self, server: ServerResponseSingle, player: ServerPlayer):
        found: List[Player] = list()
        for _player in self.players:
            for _server in _player.seen_on:
                for _identifier in _server.identifiers:
                    for identifier in player.identifiers:
                        if _identifier.identifier == identifier:
                            found.append(_player)
        if len(found) < 1:
            self.players.append(Player.from_ServerPlayer(server, player))
            return
        elif len(found) > 1:
            found_players = ", ".join([x.seen_on[0].names[0].name for x in found])
            raise Exception(f"Found more than one player to update: {found_players}")
        now = datetime.now()
        toupdate = found[0].seenOnById(server.end_point)
        toupdate.update_name(player.name, now)
        # TODO: Other update methods



def players_from_list(s: Any) -> List[Player]:
    return from_list(Player.from_dict, s)


def players_to_list(x: List[Player]) -> Any:
    return from_list(lambda x: to_class(Player, x), x)
