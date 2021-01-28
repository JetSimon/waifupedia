import json, random, jsonpickle, wikipedia

class User(object):
    def __init__(self, name):
        self.name = name
        self.money = 100
        self.harem = []
    
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
    p = wikipedia.page(wikipedia.random())
    while ("disambiguation" in p.title or len(p.images) == 0 or "svg" in p.images[0] or "ogg" in p.images[0]):
        p = wikipedia.page(wikipedia.random())
    w = Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
    return w
 
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