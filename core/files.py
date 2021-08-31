import os
import json
import datetime
import shutil
debug = True 

def check_game(name, serverID):
  with open("games/game directory.json", "r") as file:
    data = json.load(file)
    print(data["games"].get(str(serverID)))
    if data["games"].get(str(serverID)) == None:
      print("ok")
      return 
    else:
      print(data["games"][str(serverID)])
      if name in data["games"].values():
        return "name used"
      return "has game"

    
def games():
  with open("games/game directory.json", "r") as file:
    data = json.load(file)
    return data["games"].values()

def create_game(name, serverID, gameType):
  # Create new game folder, test if one of the same name already exists
  try:
    os.mkdir(f'games/{name}')
  except FileExistsError:
    print("Game name exists")
    if debug:
      print("Debug mode, overwriting game")
    else:
      return

  f = open(f'games/{name}/{name} config.json', "w")
  f.close

  with open("templates/game_info.json") as file:
    with open(f'games/{name}/{name} config.json', 'r+') as jfile:
      data = json.load(file)
      data["hostServer"] = serverID
      data["startDate"] = datetime.date.today().strftime("%b-%d-%Y")
      data["gameType"] = gameType
      json.dump(data, jfile, indent=4)
  
  with open("games/game directory.json", "r+") as file:
    data = json.load(file)
    data["games"][serverID] = name
    
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()

def end_game(name, serverID):
  with open("games/game directory.json", "r+") as file:
    data = json.load(file)
    if data["games"].get(serverID) != None:
      data["games"].pop(serverID)
    
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()
  shutil.rmtree(f"games/{name}")


def game_roles(serverID):
  with open("games/game directory.json") as file:
    data = json.load(file)
    name = data["games"][str(serverID)]
  with open(f"games/{name}/{name} config.json") as file:
    data = json.load(file)
    return data["roles"]


#start_game("id test", 69420)