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
		self.factions = {}
		self.faction_limit = 20
		self.servers = []
		self.users = {}
		self.map_bytes = ""
		self.map_name = ""
		self.game_json = {}
		self.trades = {}
		self.schedule = "* * * * *"
		self.current_claims = {}
		self.description = ""
		self.action_limit = 1
		self.invite_link = ""
		self.faction_id_counter = 0
		self.attacks={}
		r_test.add_game(name, self)

	def faction_names(self):
		output = [self.factions[i].name for i in list(self.factions.keys())]
		return output

	def get_faction(self, name=None, id=None):
		if name != None:
			for i in list(self.factions.keys()):
				if self.factions[i].name == name:
					print(f"A FACTION: {self.factions[i].name}|")
				#print(f"{name}|")
			output = [self.factions[i] for i in list(self.factions.keys()) if self.factions[i].name == name]

		elif id != None:
			output = [self.factions[i] for i in list(self.factions.keys()) if self.factions[i].id == id]
		if len(output)!=0:
			return output[0]

	def create_faction(self, name):
		if name not in self.faction_names():

			self.faction_id_counter += 1
			faction = Faction(name, self.faction_id_counter)
			self.factions[self.faction_id_counter] = faction
			print("done")
			self.save()
			
			return "Faction successfully created"
		else:
			return "Faction name already exists"

	def map(self):
		print(self.map_bytes == "")
		if self.map_bytes == "":
			self.map_bytes = r_test.map_image(self.map_name)
			print("redrawing map")
			self.redraw_map()
		print("Returning map")
		return Image.open(io.BytesIO(base64.b64decode(self.map_bytes)))
		
	#return "No map"

	def add_map(self, name):
		if r_test.map_json(name) != "Invalid JSON" and r_test.map_image(
		    name) != "Invalid Image":
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
		temp = Image.open(
		    io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))

		for i in coordinates:
			image.quick_fill(temp, eval(i), tuple(faction.colors))
		self.update_map(temp)
		return "Sucessfully claimed"

	def claim(self, id, faction):
		print("CLAIMING")
		print(faction)
		if not self.verify_id(id):
			return "Invalid ID"
		if self.game_json[id] == faction.id or self.current_claims.get(id) or self.game_json[id] != 0:
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
		temp = Image.open(io.BytesIO(base64.b64decode(r_test.map_image(self.map_name)))).convert('RGB')
		for i in self.game_json.keys():
			owner = self.game_json[i]
			if owner != 0:
				coordinates = r_test.map_json(self.map_name)[f"l{i}"]["coordinates"]
				print(coordinates)
				if self.factions.get(owner):
					faction = self.factions[owner]
				else:
					continue
				for j in coordinates:
					print(faction.colors)
					image.quick_fill(temp, eval(j), tuple(faction.colors))
					
		for i in self.current_claims.keys():
			owner = self.current_claims[i]
			if owner != 0:
				coordinates = r_test.map_json(
				    self.map_name)[f"l{i}"]["coordinates"]
				faction = self.factions[owner]
				#print(faction)
				for j in coordinates:
					image.quick_fill(temp, eval(j), tuple(faction.colors))
		self.update_map(temp)
		print("finished redraw")
		return temp

	def current_claims_map(self):
		#BROKEN RIGHT NOW, IN PROGRESS
		temp = Image.open(
		    io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))

		for i in self.current_claims.keys():
			owner = self.current_claims[i]
			if owner != 0:
				coordinates = r_test.map_json(
				    self.map_name)[f"l{i}"]["coordinates"]
				faction = self.factions[owner]
				#print(faction)
				for j in coordinates:
					image.quick_fill(temp, eval(j), tuple(faction.colors))
		#self.update_map(temp)
		print("finished redraw")
		return temp

	def fill_map(self):
		temp = Image.open(
		    io.BytesIO(base64.b64decode(r_test.map_image(self.map_name))))
		data = r_test.map_json(self.map_name)

		def temp_fill(coords):
			image.quick_fill(temp, eval(coords), (0, 0, 255))

		#with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
			#executor.map(temp_fill, coords)

	def add_faction_server(self, server_id, faction):
		if faction not in self.faction_names():
			return "Invalid Faction"
		target_faction = self.get_faction(faction)

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
		#print("USER LIST")
		#print(self.users)
		print("get_user func")
		if self.users.get(id) == None:
			user = User(id)
			self.users[id] = user
			self.save()
		#print(self.users[id].id)
		print("done with get_user")
		return self.users[id]

	def game_size(self):
		return len(r_test.pack(self).encode('utf-16'))


""""
            
    def edit_province(self, id, owner_id):
        if verify_id(id):
            self.game_json[id] = owner_id


"""

color_list = [[0, 0, 255], [255, 128, 0], [255, 255, 0], [128, 255, 0],
              [0, 255, 0], [0, 255, 128], [255, 0, 0], [0, 255, 255],
              [128, 0, 255], [255, 0, 255]]


class Faction:
	def __init__(self, name, faction_id):
		self.name = name
		self.server_id = 0
		self.users = []
		self.claims = {}
		try:
			self.colors = color_list[faction_id]
		except:
			self.colors = [
			    random.randint(1, 254),
			    random.randint(1, 254),
			    random.randint(1, 254)
			]
		self.id = faction_id
		self.roles = [
		    Roles(f"{name} Leader", 1, self),
            Roles(f"{name} Lieutenant", 2, self),
		    Roles(f"{name} Upper Midrank", 3, self),
			Roles(f"{name} Midrank", 4, self),
		    Roles(f"{name} Member", 5, self),
		    Roles(f"{name}", 6, self),
			Roles(f"{name} Applicant", 7, self)
		]

	def connect_server(self, id):
		if self.server_id == 0:
			self.server_id = id
			return "Faction successfully connected"
		elif self.server_id == id:
			return "Faction already connected to this server"
		else:
			return "Faction already connected to another server"

	def create_role(self, name):
		self.roles.append(Roles(name, len(self.roles)))

	def find_role(self, discord_id):
		print(self)
		print(self.roles)
		for i in self.roles:
			if i.central_discord_id or i.satellite_discord_id == discord_id:
				return i


class Roles:
	def __init__(self, name, id, faction):
		self.central_name = name
		self.satellite_name = name
		self.perm_id = id
		self.faction = faction.name
		self.central_id = 0
		self.satellite_id = 0
		self.colors = [0, 0, 0]
		self.perms = []


class User:
	def __init__(self, discord_id):
		self.name = ""
		self.discord_id = discord_id
		self.id = 00
		self.actions = 0
		self.claims = []
		self.rank = ""
		self.money = 0
		self.faction = ""
