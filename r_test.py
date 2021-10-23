from rejson import Client, Path
#from class_playground import Game
import pickle
import time
import codecs
import json
import base64 
r = Client(host='redis-10479.c1.us-east1-2.gce.cloud.redislabs.com', port=10479, 
                password='NbsZnTMvTwOIEmhwDAYHZZ610cTS6poY', decode_responses=True)

#print(r.execute_command("CONFIG SET MAXMEMORY 1000"))


test_json = {
  "status": "config",
  "hostServer": 0,
  "startDate": "N/A",
  "gameType": "N/A",
  "roles": "none"
}
direc = {}

def pack(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode()
def unpack(obj):
    return pickle.loads(codecs.decode(obj.encode(), "base64"))


def save_game(name, obj):
    if r.jsonget("games", Path.rootPath()) == None:
        r.jsonset("games", Path.rootPath(), {})
        
    print("SAVING")
    print(name)

    directory = r.jsonget("games", Path.rootPath())

    directory[name] = pack(obj)
    #print(unpack(directory[name]).factions)
    r.jsonset("games", Path.rootPath(), directory)
    load_game_object(name)
    print("SAVED")

def add_game(name, obj):
    if r.jsonget("games", Path.rootPath()) == None:
        r.jsonset("games", Path.rootPath(), {})
    directory = r.jsonget("games", Path.rootPath())
    if name in directory:
        return "Name already in use"
    
    directory[name] = pack(obj)
    r.jsonset("games", Path.rootPath(), directory)

    #print(r.jsonget("game_directory",Path.rootPath()))
    return "Game Added"


def load_game_object(name):
    if r.jsonget("games", Path.rootPath()) == None:
        r.jsonset("games", Path.rootPath(), {})
    directory = r.jsonget("games", Path.rootPath())
    return unpack(directory[name])

def strip_json(json_obj):
    removal_keys = []
    recreate_keys = []
    for i in json_obj.keys():
        if i[0] == "w":
            removal_keys.append(i)
        if i[0] == "l":
            recreate_keys.append(i[1:])
    new_json = {}
    for i in recreate_keys:
        new_json[i] = 0
    return new_json

def upload_map_json(name):

    if r.jsonget("map_jsons", Path.rootPath()) == None:
        r.jsonset("map_jsons", Path.rootPath(), {})

    objects = r.jsonget("map_jsons", Path.rootPath())
    with open(f"{name}.json") as file:
        data = json.load(file)
        objects[name] = data
    r.jsonset("map_jsons", Path.rootPath(), objects)
    print("JSON uploaded")

def upload_map_image(name):
        if r.jsonget("map_images", Path.rootPath()) == None:
            r.jsonset("map_images", Path.rootPath(), {})
        objects = r.jsonget("map_images")
    
        with open(f"{name}.png", "rb") as image2string:
            #print(base64.b64encode(image2string.read()).decode())
            objects[name] = base64.b64encode(image2string.read()).decode()
            r.jsonset("map_images", Path.rootPath(), objects)
        print("Image uploaded")

def map_image(name):
    if r.jsonget("map_images", Path.rootPath()) == None:
        r.jsonset("map_images", Path.rootPath(), {})
        return "Invalid Image"
    response = r.jsonget("map_images", Path(f".{name}")) 
    if response != None:
        return response
    else:
        return "Invalid Image"
def map_json(name):
    if r.jsonget("map_jsons", Path.rootPath()) == None:
        r.jsonset("map_jsons", Path.rootPath(), {})
        return "Invalid JSON"
    response = r.jsonget("map_jsons", Path(f".{name}")) 
    if response != None:
        return response
    else:
        return "Invalid JSON"


def load_from_id(id):
    if r.jsonget("games", Path.rootPath()) == None:
        r.jsonset("games", Path.rootPath(), {})
    games = r.jsonget("games", Path.rootPath())
    for i in games.keys():
        game = unpack(games[i])
        if game.server_id == id:
            return game
    return None

def games():
    return r.jsonget("games", Path.rootPath()).keys()
#print(r.jsonget("test2", Path('.startDate')))

