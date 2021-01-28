import json, random, jsonpickle, wikipedia, datetime

ROLL_TIME = 30
class User(object):
    def __init__(self, name):
        self.name = name
        self.money = 0
        self.harem = []
        self.wishlist = []
        self.lastRolled = datetime.datetime(1970, 1, 2)
    
    def CanRoll(self):
        return ((datetime.datetime.now() - self.lastRolled).total_seconds()) > ROLL_TIME
    
    def TimeToRoll(self):
        return int(ROLL_TIME - (datetime.datetime.now() - self.lastRolled).total_seconds())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Waifu(object):
    def __init__(self, name, image, value, desc, url):
        self.image = image
        self.name = name
        self.desc = desc
        self.value = value
        self.url = url
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def GenerateWaifu():
    try:
        p = wikipedia.page(wikipedia.random())
    except wikipedia.DisambiguationError as e:
        s = random.choice(e.options)
        p = wikipedia.page(s)
    while (len(p.images) == 0 or "svg" in p.images[0] or "ogg" in p.images[0]):
        try:
            p = wikipedia.page(wikipedia.random())
        except wikipedia.DisambiguationError as e:
            s = random.choice(e.options)
            p = wikipedia.page(s)
    w = Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
    return w
 
def SearchFor(s):
    try:
        p = wikipedia.page(title=wikipedia.search(s, results=1, suggestion=False)[0])
    except wikipedia.DisambiguationError as e:
        s = random.choice(e.options)
        p = wikipedia.page(s)
    except wikipedia.PageError:
        return False
    return p

def Save(users, waifus):
    with open('users.json', 'w') as fp:
        u=jsonpickle.encode(users)
        fp.write(u)
    with open('waifus.json', 'w') as fp:
        u=jsonpickle.encode(waifus)
        fp.write(u)

def GetUser(users,name):
    for user in users:
        if user.name == name:
            return user
    return False

def GetRules():
    rules = ["%w/%wiki - roll a waifu", "%divorce WAIFUNAME- divorce a waifu for money", "%divorceall divorce all waifus are married to"
    ,"%buy WAIFUNAME - buy any waifu if you have the money", "%im WAIFUNAME - search for a waifu", "%harem - view all waifus you are currently married to"
    ,"%$/%money - see all your wikibucks you have", "%wish WAIFUNAME - add waifu to your wishlist", "%wishremove WAIFUNAME - remove waifu from your wishlist", "%wishlist - view your wishlist"]
    out=""
    for rule in rules:
        out += " - " + rule + "\n"
    return out