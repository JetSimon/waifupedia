import json, random, jsonpickle, wikipedia, datetime, discord

ROLL_TIME = 10


class Waifu(object):
    def __init__(self, name, image, value, desc, url):
        self.image = image
        self.name = name
        self.desc = desc
        self.value = value
        self.url = url
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class User(object):
    def __init__(self, name, img, id):
        self.id = str(id)
        self.img = img
        self.name = name
        self.money = 0
        self.harem = []
        self.wishlist = []
        self.lastRolled = datetime.datetime(1970, 1, 2)
    
    def UpdateProfilePic(self, url):
        self.img = url

    def CanRoll(self):
        return ((datetime.datetime.now() - self.lastRolled).total_seconds()) > ROLL_TIME
    
    def TimeToRoll(self):
        return int(ROLL_TIME - (datetime.datetime.now() - self.lastRolled).total_seconds())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def GetOwner(waifu, users):
    for user in users:
        for w in user.harem:
            if(w.name == waifu.name):
                print("owner is "+ user.name)
                return user
    return None

def WaifuEmbed(w, users):
    embed=discord.Embed(title=(w.name + " - " + "$" + str(w.value)), description=w.desc, color=0xFF5733, url=w.url)
    embed.set_image(url=w.image)

    user = GetOwner(w, users)

    if(user != None):
        embed.set_author(name="married to " + user.name,icon_url=user.img)

    return embed

def GetHaremPageLength(harem):
    return str(len(HaremToPages(harem)))

def UpdateUserInfo(users):
    if(users != []):
        for user in users:
            user.UpdateProfilePic()

def HaremToPages(harem):
    out = []
    current = []

    for w in harem:
        current.append(w)
        if(len(current) >= 10):
            out.append(current)
            current = []

    if(len(current) != 0):
        out.append(current)
    
    return out

def GetValueOfHarem(harem):
    out=0
    for w in harem:
        out+=w.value
    return out

def RenderList(harem):
    totalVal = GetValueOfHarem(harem)
    out=""
    for w in harem:
            out+= "- **" + w.name + "** ($" + str(w.value) + ")\n"
    return out

def NextPage(l, current):
    if(current + 1 <= int(GetHaremPageLength(l))-1):
        return current + 1
    return current

def PrevPage(l, current):
    if(current - 1 >= 0):
        return current - 1
    return current

def GenerateWaifuFromPool(waifuPool):

    if(len(waifuPool) <= 0):
        return waifutools.GenerateWaifu()


    w = random.choice(waifuPool)
    waifuPool.remove(w)
    return w

def GenerateWaifu():
    print("Generating Waifu...")
    errorThrown = False
    try:
        p = wikipedia.page(wikipedia.random(), preload=True)
    except wikipedia.DisambiguationError as e:
        errorThrown = True
        s = random.choice(e.options)
        p = wikipedia.page(s, preload=True)
    except wikipedia.exceptions.PageError as e:
        errorThrown = True

    while (errorThrown or len(p.images) == 0 ):
        errorThrown = False
        try:
            p = wikipedia.page(wikipedia.random(), preload=True)
        except wikipedia.DisambiguationError as e:
            errorThrown = True
            s = random.choice(e.options)
            p = wikipedia.page(s, preload=True)
        except wikipedia.exceptions.PageError as e:
            errorThrown = True

    val = int((len(p.content) / 100))
    w = Waifu(p.title, p.images[0], val, p.summary.split(".")[0], p.url)
    print("DONE GENERATION!")
    return w
 
def SearchFor(s):
    try:
        p = wikipedia.page(title=wikipedia.search(s, results=1, suggestion=False)[0], preload=True)
    except wikipedia.DisambiguationError as e:
        s = random.choice(e.options)
        p = wikipedia.page(s, preload=True)
    except wikipedia.PageError:
        return False
    return p

def Save(users):
    with open('users.json', 'w') as fp:
        u=jsonpickle.encode(users)
        fp.write(u)

def GetUser(users,name):
    if("@" not in name):
        for user in users:
            if user.name == name:
                return user
    else:
        for user in users:
            if user.id == name.replace("<","").replace(">","").replace("@","").replace("!",""):
                return user
    return False

def GetRules():
    rules = ["%w/%wiki - roll a waifu", "%divorce WAIFUNAME- divorce a waifu for money", "%divorceall divorce all waifus are married to"
    ,"%buy WAIFUNAME - buy any waifu if you have the money", "%im WAIFUNAME - search for a waifu", "%harem - view all waifus you are currently married to", "%harem USER - view all waifus a user currently married to"
    ,"%$/%money - see all your wikibucks you have", "%wish WAIFUNAME - add waifu to your wishlist", "%wishremove WAIFUNAME - remove waifu from your wishlist", "%wishlist - view your wishlist", "%give WAIFUNAME:USER"]
    out=""
    for rule in rules:
        out += " - " + rule + "\n"
    return out

