import os,io,json,random,discord,waifutools,jsonpickle,asyncio,datetime
from dotenv import load_dotenv

POOL_SIZE = 2

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

users = []

waifuPool = []

for i in range(POOL_SIZE):
    print("Generating Waifu " + str(i + 1))
    waifuPool.append(waifutools.GenerateWaifu())


if os.path.isfile('users.json'):
    print("users file found")
    with open('users.json', 'r') as fp:
        u = fp.read()
        users = jsonpickle.decode(u)


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
        user = waifutools.User(message.author.name, str(message.author.avatar_url), message.author.id)
        users.append(user)
    else:
        user = userAttempt
        user.UpdateProfilePic(str(message.author.avatar_url))

    if message.content == '%w' or message.content == '%wiki':
        print (user.betterwish)
        if(user.CanRoll()):
            await message.channel.send("Rolling up a waifu for " + user.name + "...")
            user.lastRolled = datetime.datetime.now()

            if(((user.betterwish > 0 and random.randint(0,35) == 10) or random.randint(0,100) == 50) and len(user.wishlist) > 0):
                w = random.choice(user.wishlist)
            else:
                w = waifutools.GenerateWaifuFromPool(waifuPool)

            if user.betterwish > 0:
                user.betterwish -= 1

            embed=waifutools.WaifuEmbed(w,users)
            msg = await message.channel.send(embed=embed)

            if(waifutools.GetOwner(w, users) != None):
                return

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

            
            waifutools.Save(users)

        else:
            await message.channel.send(user.name + ", you must wait " + str(user.TimeToRoll()) + " seconds to roll!")
    else:
        if(len(waifuPool) < POOL_SIZE):
            waifuPool.append(waifutools.GenerateWaifu())
    if message.content == "%help":
        embed=discord.Embed(title="LIST OF COMMANDS", description=waifutools.GetRules(), color=0xFF5733)
        await message.channel.send(embed=embed)
    
    if message.content == "%$" or message.content == "%money":
        await message.channel.send("You currently have $" + str(user.money) + " wikibucks!")
    
    if message.content[0:4] == "%use":
        toUse = message.content.split(" ", 1)[1]
        if toUse in user.inventory:
            user.UseItem(toUse)
            await message.channel.send("Used " + toUse + "!")
        else:
            await message.channel.send("You do not have any " + toUse + "!")
        return
    
    if message.content == "%inventory" or message.content == "%inv":
        embed=discord.Embed(title=user.name + "'s Inventory", description=waifutools.GetInventory(user), color=0xFF5733)
        embed.set_author(name=user.name,icon_url=user.img)
        msg = await message.channel.send(embed=embed)
        return

    if message.content[0:6] == "%harem":
        haremOwner = user

        if(" " in message.content):
            searched = message.content.split(" ", 1)[1]
          
            haremOwner = waifutools.GetUser(users, searched)
            if(haremOwner == False):
                await message.channel.send("Cannot find user by the name of " + searched)
                return

        l = waifutools.HaremToPages(haremOwner.harem)
        i = 0
        out = (waifutools.RenderList(l[i]) + "\nTotal Value: $" + str(waifutools.GetValueOfHarem(haremOwner.harem)))

        embed=discord.Embed(title=haremOwner.name + "'s Harem ("+ str(i+1) +"/"+ waifutools.GetHaremPageLength(haremOwner.harem)  + ")", description=out, color=0xFF5733)
        embed.set_author(name=haremOwner.name,icon_url=haremOwner.img)
        msg = await message.channel.send(embed=embed)

        await msg.add_reaction("◀")
        await msg.add_reaction("▶")

        def reacted(reaction, u):
            return (str(reaction.emoji) == "▶" or str(reaction.emoji) == "◀") and u != client.user

        acceptingInput = True
        while acceptingInput:
            try:
                reaction, u = await client.wait_for('reaction_add', timeout=10.0, check=reacted)
            except asyncio.TimeoutError:
                print("out of time!")
                acceptingInput = False
            else:
                acceptingInput = True
                await reaction.remove(u)
                
                
                if(str(reaction.emoji) == "▶"):
                    i = waifutools.NextPage(haremOwner.harem, i)
                elif (str(reaction.emoji) == "◀"):
                    i = waifutools.PrevPage(haremOwner.harem, i)
                embed.description = (waifutools.RenderList(l[i]) + "\nTotal Value: $" + str(waifutools.GetValueOfHarem(haremOwner.harem)))
                embed.title = haremOwner.name + "'s Harem ("+ str(i+1) +"/"+ waifutools.GetHaremPageLength(haremOwner.harem)  + ")"
                print(i)
                await msg.edit(embed=embed)

    if message.content[0:6] == "%shop":
        out, items = waifutools.GetShop()
        embed=discord.Embed(title="Shop o' Wares (WORK IN PROGRESS)", description=out, color=0xadd8e6)
        embed.set_image(url="https://media.pri.org/s3fs-public/styles/open_graph/public/images/2020/04/2020-4-20-nycbodega-nassimalmontaser_1.jpg?itok=cvfUVF3d")
        msg = await message.channel.send(embed=embed)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")

        def reacted(reaction, u):
            return (str(reaction.emoji) == "1️⃣" or str(reaction.emoji) == "2️⃣" or str(reaction.emoji) == "3️⃣" or str(reaction.emoji) == "4️⃣") and u != client.user

        acceptingInput = True
        while acceptingInput:
            try:
                reaction, u = await client.wait_for('reaction_add', timeout=30.0, check=reacted)
            except asyncio.TimeoutError:
                print("out of time!")
                acceptingInput = False
            else:
                acceptingInput = True
                await reaction.remove(u)
                
                r = waifutools.GetUser(users, u.name)
                if(str(reaction.emoji) == "1️⃣"):
                    if(r.money >= 300):
                        r.money -= 300
                        r.betterwish += 5
                        await message.channel.send("**" + u.name + "**" + " bought Wishing Fluid!")
                    else:
                        await message.channel.send("**" + u.name + "**" + ", not enough money!")
                elif(str(reaction.emoji) == "2️⃣"):
                    if(r.money >= 2000):
                        r.money -= 2000
                        r.inventory["Death Note Page"] = 1 if "Death Note Page" not in r.inventory else r.inventory["Death Note Page"] + 1
                        await message.channel.send("**" + u.name + "**" + " bought Death Note Page!")
                    else:
                        await message.channel.send("**" + u.name + "**" + ", not enough money!")
                elif(str(reaction.emoji) == "3️⃣"):
                    if(r.money >= 69):
                        r.money -= 69
                        waifutools.GetUser(users, "SimonJet").money += 69
                        await message.channel.send("**" + u.name + "**" + " donated $69 to Jet!")
                    else:
                        await message.channel.send("**" + u.name + "**" + ", not enough money!")
                elif(str(reaction.emoji) == "4️⃣"):
                    await message.channel.send("This one does nothing yet!")
        return


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
        waifutools.Save(users)

    if message.content.split(" ")[0] == "%im":
        toSearch = message.content.split(" ", 1)[1]
        p = waifutools.SearchFor(toSearch)
        if(p == False):
            await message.channel.send(user.name + ", I did not find a page by the name of " + toSearch)
            return
        w = waifutools.Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
        embed = waifutools.WaifuEmbed(w,users)
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

        if(len(user.wishlist) <= 10):  
            user.wishlist.append(w)
            msg = await message.channel.send("**"+user.name + "** has wished for **" + w.name+"**")
            waifutools.Save(users)
        else:
            msg = await message.channel.send("**"+user.name + "**, you may only wish for 10 waifus at a time.")

    if message.content.split(" ")[0] == "%buy":
        toSearch = message.content.split(" ", 1)[1]
        p = waifutools.SearchFor(toSearch)
        if(p == False):
            await message.channel.send(user.name + ", I did not find a page by the name of " + toSearch)
            return
        w = waifutools.Waifu(p.title, p.images[0], int(len(p.content) / 100), p.summary.split(".")[0], p.url)
        
        if(waifutools.GetOwner(w, users) != None):
            await message.channel.send(w.name + " is already married.")
            return

        for wife in user.harem:
            if(wife.name == w.name):
                msg = await message.channel.send(user.name + ", you are already married to " + w.name)
                return
                
        if(user.money >= w.value):
            user.harem.append(w)
            user.money -= w.value
            msg = await message.channel.send("**"+user.name + "** has married **" + w.name + "** for $" + str(w.value) +"! $" + str(user.money) + " remaining!")
            
            waifutools.Save(users)
        else:
            msg = await message.channel.send(user.name + ", you do not have the money for " + w.name + ", that waifu costs $" + str(w.value))

    if message.content.split(" ")[0] == "%give":
        toSearch = message.content.split(" ", 1)[1].split(":")[0].strip()
        toGiveTo = message.content.split(" ", 1)[1].split(":")[1].strip()
       
        for wife in user.harem:
            if(wife.name.lower().strip() == toSearch.lower().strip()):
                w = wife
                u = waifutools.GetUser(users, toGiveTo)
                if(u != False):
                    u.harem.append(w)
                    user.harem.remove(w)
                    msg = await message.channel.send("**" + user.name + "** has given **" + w.name + "** to **" + u.name + "**")
                    return
                await message.channel.send(toGiveTo + " is not a user")
                return

        await message.channel.send(user.name + ", you are not married to " + toSearch)
        return

    
    if message.content.split(" ")[0] == "%wishremove":
        toDivorce = message.content.split(" ", 1)[1]
        for w in user.wishlist:
            if(w.name.lower().strip() == toDivorce.lower().strip()):
                await message.channel.send("**"+user.name + "** has removed **" + w.name + "** from their wishlist")
                user.wishlist.remove(w) 
                return
        await message.channel.send(user.name + ", you are not wishing for " + toDivorce)
        waifutools.Save(users)

    if message.content == "%divorceall":
        totalVal = 0
        for w in user.harem:
            totalVal += w.value
        user.money += totalVal
        user.harem = []
        waifutools.Save(users)
        await message.channel.send(user.name + " has cleansed their harem for $" + str(totalVal))
    
    if message.content[0:5] == "%kill":
        if(user.inventory["Death Note Page"] > 0):
            user.inventory["Death Note Page"] -= 1
            target = message.content.split(" ", 1)[1]
            await message.channel.send(waifutools.FindAndRemoveWaifu(users, target))
        else:
            await message.channel.send("You do not have the ability to kill a waifu")
    
    if message.content[0:4] == "%bet":
        amount = int(message.content.split(" ")[1])
        if user.money >= amount:
            user.money -= amount
            embed=discord.Embed(title="Pick A Cup!", description="Choose a cup below. If you pick the correct cup, you will double your bet of $" + str(amount), color=0xadd8e6)
            embed.set_image(url="https://i.ytimg.com/vi/luMtoqCOpT0/mqdefault.jpg")
            msg = await message.channel.send(embed=embed)

            await msg.add_reaction("🥤")
            await msg.add_reaction("☕")
            await msg.add_reaction("🍶")

            answer = random.randint(1,3)

            def reacted(reaction, u):
                return (str(reaction.emoji) == "🥤" or str(reaction.emoji) == "☕" or str(reaction.emoji) == "🍶") and u == message.author

            acceptingInput = True
            while acceptingInput:
                try:
                    reaction, u = await client.wait_for('reaction_add', timeout=30.0, check=reacted)
                except asyncio.TimeoutError:
                    print("out of time!")
                    user.money += amount
                    acceptingInput = False
                else:
                    acceptingInput = False
                    await reaction.remove(u)
                    if(answer == 1):
                        user.money += amount *2
                        await message.channel.send("You won! You have doubled your bet of **$" + str(amount) +"** to **$" + str(amount * 2) + "**! 💰💰💰")
                        return
                    await message.channel.send("Dang! That was the wrong cup. Better luck next time! 🙏")
                    
        else:
            await message.channel.send("You cannot bet that much money")
    


client.run(TOKEN)

