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
            user.lastRolled = datetime.datetime.now()
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
                await message.channel.send(u.name + " has married " + w.name + "!")
                waifutools.GetUser(users, u.name).harem.append(w)

            waifus.append(w)
            waifutools.Save(users, waifus)

        else:
            await message.channel.send(user.name + ", you must wait " + str(user.TimeToRoll()) + " seconds to roll!")
        
    
    if message.content == "%$":
        await message.channel.send("You currently have $" + str(user.money) + " wikibucks!")

    if message.content == "%harem":
        out = user.name + "'s Harem:\n"
        for w in user.harem:
            out+= "- **" + w.name + "** ($" + str(w.value) + ")\n"
        await message.channel.send(out)

    if message.content.split(" ")[0] == "%divorce":
        toDivorce = message.content.split(" ", 1)[1]
        for w in user.harem:
            if(w.name == toDivorce):
                await message.channel.send(user.name + " has divorced " + w.name + " for $" + str(w.value))
                user.money += w.value
                user.harem.remove(w) 
                return
        await message.channel.send(user.name + ", you are not married to " + toDivorce)

    if message.content == "%divorceall":
        totalVal = 0
        for w in user.harem:
            totalVal += w.value
        user.money += totalVal
        user.harem = []
        await message.channel.send(user.name + " has cleansed their harem for $" + str(totalVal))
        



client.run(TOKEN)

