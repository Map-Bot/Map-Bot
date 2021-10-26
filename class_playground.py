import r_test
import json
from PIL import Image
import image
import base64
import io
import random
import threading
import concurrent.futures

class Game:
    def save(self):
        r_test.save_game(self.name, self)
        
    def __init__(self, name, server_id, central=True):
        self.name = name
        self.central = central
        self.server_id = server_id
        self.factions = []
        self.servers = []
        self.users = []
        self.map_bytes = ""
        self.map_name = ""
        self.game_json = {}
        self.trades = {}
        self.schedule = None
        self.current_claims={}
        self.description = ""
        self.invite_link = ""
        r_test.add_game(name, self)

    def faction_names(self):
        output = [i.name for i in self.factions]
        return output

    def get_faction(self, name):
        output = [i for i in self.factions if i.name == name]
        if output != []:
            return output[0]

        
    def create_faction(self, name):
        if name not in self.faction_names():
            faction = Faction(name, len(self.factions)+1)
            self.factions.append(faction)
            self.save()
            return "Faction successfully created"
        else:
            return "Faction name already exists"

    
    def map(self):
        return Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))
        if self.map_bytes != "":
            return Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))
        else:
            return "No map"


    def add_map(self, name):
        if r_test.map_json(name) != "Invalid JSON" and r_test.map_image(name) != "Invalid Image":
            self.map_name = name
            self.game_json = r_test.strip_json(r_test.map_json(name))
            #self.map_bytes = r_test.map_image(name)
            self.save()
            return f"Sucessfully added map: {name}"
        else:
            return "Invalid JSON"
            #self.map_bytes = Image.open(name).tobytes()
        self.save()

    def update_map(self, image):
        image.save("temp_map.png")
        with open(f"temp_map.png", "rb") as image2string:
            self.map_bytes = base64.b64encode(image2string.read()).decode()
        print("Map updated")
        self.save()


    def verify_id(self, id):
        if self.game_json.get(f"{str(id)}") != None:
            return True
        else:
            return False

    def edit_province(self, id, faction):
        if not self.verify_id(id):
            return "Invalid ID"
        if self.game_json[id] != 0:
            return "Province already claimed"
        print(self.game_json[id])
        self.game_json[id] = faction.id
        coordinates = r_test.map_json(self.map_name)[f"l{id}"]["coordinates"]
        print(faction.colors)
        temp = self.map()
        
        for i in coordinates:
            image.quick_fill(temp, eval(i), tuple(faction.colors))
        print("coordinates done")
        self.update_map(temp)
        return "Sucessfully claimed"

    def claim(self, id, faction):
        if not self.verify_id(id):
            return "Invalid ID"
        if self.game_json[id] != 0 or self.current_claims.get(id) != None :
            return f"Province already {id} claimed"
        print(self.game_json[id])
        self.current_claims[id] = faction.id
        coordinates = r_test.map_json(self.map_name)[f"l{id}"]["coordinates"]
        print(faction.colors)
        
        temp = self.map()
        
        for i in coordinates:
            image.quick_fill(temp, eval(i), tuple(faction.colors))
        print("coordinates done")
        self.update_map(temp)
        return "Sucessfully claimed"

    def add_schedule(self, cron):
        self.schedule = cron
        print("schedule added")

    def end_schedule(self):
        if self.schedule != None:
            self.schedule = None
    
    def redraw_map(self):
        print("began redraw")
        temp = Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))
        for i in self.game_json.keys():
            owner = self.game_json[i]-1
            if owner != -1:
                coordinates = r_test.map_json(self.map_name)[f"l{i}"]["coordinates"]
                faction = self.factions[owner]
                #print(faction)
                for j in coordinates:
                    image.quick_fill(temp, eval(j), tuple(faction.colors))
        for i in self.current_claims.keys():
            owner = self.current_claims[i]-1
            if owner != -1:
                coordinates = r_test.map_json(self.map_name)[f"l{i}"]["coordinates"]
                faction = self.factions[owner]
                #print(faction)
                for j in coordinates:
                    image.quick_fill(temp, eval(j), tuple(faction.colors))
        self.update_map(temp)
        print("finished redraw")
        return temp

    def current_claims_map(self):
        #BROKEN RIGHT NOW, IN PROGRESS
        temp = Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))

        for i in self.current_claims.keys():
            owner = self.current_claims[i]-1
            if owner != -1:
                coordinates = r_test.map_json(self.map_name)[f"l{i}"]["coordinates"]
                faction = self.factions[owner]
                #print(faction)
                for j in coordinates:
                    image.quick_fill(temp, eval(j), tuple(faction.colors))
        self.update_map(temp)
        print("finished redraw")
        return temp
    
    def fill_map(self):
        temp = Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))
        data = r_test.map_json(self.map_name)

        def temp_fill(coords):
            image.quick_fill(temp, eval(coords), (0,0,255))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(temp_fill, coords)

    def add_faction_server(self, server_id, faction):
        if faction not in self.faction_names():
            return "Invalid Faction"
        target_faction = [i for i in self.factions if i.name == faction][0]

        if target_faction.connect_server(server_id) != None:
            return target_faction.connect_server(server_id)
        
        self.servers.append(server_id)
        return "Faction server successfully added"
        
    def add_json(self, name):
        if r_test.map_json(name) != "Invalid JSON":
            self.source_json = name
            self.game_json = r_test.strip_json(r_test.map_json(name))
            self.save()
        else:
            return "Invalid JSON"
    
    def get_user(self, id):
        print(self.users)
        for index, i in enumerate(self.users):
            if i.id == 00:
                    i.id = index
            if i.discord_id == id:                
                return i
        print("Creating new user")
        user = User(id)
        print(user.id)
        user.id = len(self.users)
        self.users.append(user)
        self.save()
        return user
    
    def game_size(self):
        return len(r_test.pack(self).encode('utf-16'))

""""
            
    def edit_province(self, id, owner_id):
        if verify_id(id):
            self.game_json[id] = owner_id


"""

color_list = [[0, 0, 255],[255, 128, 0],[255, 255, 0],[128, 255, 0],[0, 255, 0],[0, 255, 128],[255, 0, 0],[0, 255, 255],[128, 0, 255],[255, 0, 255]]

class Faction:
    
    def __init__(self, name, faction_id):
        self.name = name
        self.server_id = 0
        self.users = []
        self.claims = {}
        try:
            self.colors = color_list[faction_id-1]
        except:
            self.colors = [random.randint(0,255),random.randint(0,255),random.randint(0,255)]
        self.id = faction_id
        self.roles = [Roles(f"{name} Leader", 1, self),Roles(f"{name} Midrank", 2, self),Roles(f"{name} Member", 3, self), Roles(f"{name}", 3, self)]
        
    def connect_server(self, id):
        if self.server_id == 0:
            self.server_id = id 
            return "Faction successfully connected"
        elif self.server_id == id:
            return "Faction already connected to this server"
        else:
            return "Faction already connected to another server"

    def create_role(name):
        self.roles.append(Roles(name, len(self.roles)))

    def find_role(discord_id):
        for i in self.roles:
            if i.central_discord_id or i.satellite_discord_id == discord_id:
                return i

    

permissions_list = ["Trade","Claim","Leader",""]
class Roles:

    def __init__(self, name, id, faction):
        self.central_name = name
        self.satellite_name = name
        self.role_id = id
        self.faction = faction.name
        self.central_id = 0
        self.satellite_id = 0
        self.colors = [0,0,0]        
        self.perms = []



class User:
    def __init__(self, discord_id):
        self.name = ""
        self.discord_id = discord_id
        self.id = 00
        self.claims = []
        self.rank = ""
        self.money = 0
        self.faction = ""