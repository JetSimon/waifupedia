import os,io,json,random,discord,wikipedia,waifutools,jsonpickle,asyncio,datetime
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

users = []
waifus = []

if os.path.isfile('users.json'):
    print("users file found")
    with open('users.json', 'r') as fp:
        u = fp.read()
        users = jsonpickle.decode(u)

if os.path.isfile('waifus.json'):
    print("waifus file found")
    with open('waifus.json', 'r') as fp:
        u = fp.read()
        waifus = jsonpickle.decode(u)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    userAttempt = waifutools.GetUser(users, message.author.name)
    if(userAttempt == False):
        user = waifutools.User(message.author.name)
        users.append(user)
    else:
        user = userAttempt

    if message.content == '%w' or message.content == '%wiki':
        
        if(user.CanRoll()):
            await message.channel.send("Rolling up a waifu for " + user.name + "...")
            user.lastRolled = datetime.datetime.now()

            if(random.randint(0,100) == 50 and len(user.wishlist) > 0):
                w = random.choice(user.wishlist)
            else:
                w = waifutools.GenerateWaifu()
            embed=discord.Embed(title=(w.name + " - " + "$" + str(w.value)), description=w.desc, color=0xFF5733, url=w.url)
            print(w.image)
            embed.set_image(url=w.image)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("💕")

            def marry(reaction, u):
                print(u.name)
                return str(reaction.emoji) == "💕" and u != client.user and reaction.message == msg
                

            try:
                reaction, u = await client.wait_for('reaction_add', timeout=30.0, check=marry)
            except asyncio.TimeoutError:
                print("out of time!")
            else:
                await message.channel.send("**"+u.name + "** has married **" + w.name + "**!")
                waifutools.GetUser(users, u.name).harem.append(w)

            waifus.append(w)
            waifutools.Save(users, waifus)

        else:
            await message.channel.send(user.name + ", you must wait " + str(user.TimeToRoll()) + " seconds to roll!")
    
    if message.content == "%help":
        embed=discord.Embed(title="LIST OF COMMANDS", description=waifutools.GetRules(), color=0xFF5733)
        await message.channel.send(embed=embed)
    
    if message.content == "%$" or message.content == "%money":
        await message.channel.send("You currently have $" + str(user.money) + " wikibucks!")

    if message.content == "%harem":
        out = ""
        for w in user.harem:
            out+= "- **" + w.name + "** ($" + str(w.value) + ")\n"
        embed=discord.Embed(title=user.name + "'s Harem", description=out, color=0xFF5733)
        embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)

    if message.content == "%wishlist":
        out = ""
        for w in user.wishlist:
            out+= "- **" + w.name + "** ($" + str(w.value) + ")\n"
        embed=discord.Embed(title=user.name + "'s Wishlist", description=out, color=0xFF5733)
        embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)

    if message.content.split(" ")[0] == "%divorce":
        toDivorce = message.content.split(" ", 1)[1]
        for w in user.harem:
            if(w.name.lower().strip() == toDivorce.lower().strip()):
                await message.channel.send("**"+user.name + "** has divorced **" + w.name + "** for $" + str(w.value))
                user.money += w.value
                user.harem.remove(w) 
                return
        await message.channel.send(user.name + ", you are not married to " + toDivorce)
        waifutools.Save(users, waifus)

    if message.content.split(" ")[0] == "%im":
        toSearch = message.content.split(" ", 1)[1]
        p = waifutools.SearchFor(toSearch)
        if(p == False):
            await message.channel.send(user.name + ", I did not find a page by the name of " + toSearch)
            return
        w = waifutools.Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
        embed=discord.Embed(title=(w.name + " - " + "$" + str(w.value)), description=w.desc, color=0xFF5733, url=w.url)
        embed.set_image(url=w.image)
        msg = await message.channel.send(embed=embed)

    if message.content.split(" ")[0] == "%wish":
        toSearch = message.content.split(" ", 1)[1]
        p = waifutools.SearchFor(toSearch)
        if(p == False):
            await message.channel.send(user.name + ", I did not find a page by the name of " + toSearch)
            return
        w = waifutools.Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
        
        for wife in user.wishlist:
            if(wife.name == w.name):
                msg = await message.channel.send(user.name + ", you are already wishing for " + w.name)
                return
                
        user.wishlist.append(w)
        msg = await message.channel.send(user.name + " has wished for " + w.name)
        waifutools.Save(users, waifus)

    if message.content.split(" ")[0] == "%buy":
        toSearch = message.content.split(" ", 1)[1]
        p = waifutools.SearchFor(toSearch)
        if(p == False):
            await message.channel.send(user.name + ", I did not find a page by the name of " + toSearch)
            return
        w = waifutools.Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
        
        for wife in user.harem:
            if(wife.name == w.name):
                msg = await message.channel.send(user.name + ", you are already married to " + w.name)
                return
                
        if(user.money >= w.value):
            user.harem.append(w)
            msg = await message.channel.send("**"+user.name + "** has married **" + w.name + "** for $" + str(w.value) +"! $" + str(user.money) + " remaining!")
            user.money -= w.value
            waifutools.Save(users, waifus)
        else:
            msg = await message.channel.send(user.name + ", you do not have the money for " + w.name + ", that waifu costs $" + str(w.value))
    
    if message.content.split(" ")[0] == "%wishremove":
        toDivorce = message.content.split(" ", 1)[1]
        for w in user.wishlist:
            if(w.name.lower().strip() == toDivorce.lower().strip()):
                await message.channel.send(user.name + " has removed " + w.name + " from their wishlist")
                user.wishlist.remove(w) 
                return
        await message.channel.send(user.name + ", you are not wishing for " + toDivorce)
        waifutools.Save(users, waifus)

    if message.content == "%divorceall":
        totalVal = 0
        for w in user.harem:
            totalVal += w.value
        user.money += totalVal
        user.harem = []
        await message.channel.send(user.name + " has cleansed their harem for $" + str(totalVal))
        waifutools.Save(users, waifus)



client.run(TOKEN)

