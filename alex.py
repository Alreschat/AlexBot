#!/usr/bin/env python
import discord
import os
import threading
import re
import epubCreator as ec
import authentications as a


dir_path = os.path.dirname(os.path.realpath(__file__))
TOKEN = a.TOKEN


def queryWorker(query, results):
    p = ec.reqJson(query)
    if 'error' in p:
        #if(p['error'] != -1024):
            #print(p['error'])
        return 
    ficInfo = ec.metaDataString(p)
    results.append(ficInfo[0])
    return

client = discord.Client()
@client.event
async def on_message(message):
    if(str(message.author) == "Alr#5673" and message.content == "!kill alexy"):
        exit()
    message.content = re.sub(' +', ' ', message.content)
    message.content = re.sub('[<>_*]', '', message.content)
    # we do not want the bot to reply to itself
    if message.author.bot or message.author == client.user:
        return

    lookUpPrefix = 'https://alexandria.serv.pink/api/lookup/'

    if message.content.startswith('!download'):
        message.content = message.content[len('!download'):]
        query = message.content.split()[0]
        apiPrefix = 'https://alexandria.serv.pink/api/fic/'

        p = ec.reqJson(lookUpPrefix + query)
        if 'error' in p:
            await message.channel.send("Query returned with an error")
            return

        fic = p['urlId']
        ficInfo, ficName = ec.metaDataString(p)
        e = discord.Embed(title=ficName)
        msg = await message.channel.send(f"Preparing: \n{ficInfo}", embed=e)
        async with message.channel.typing():
            await message.add_reaction('👍')
            await ec.createEpub(apiPrefix + fic + '/', message.channel)
            fileMsg = await message.channel.send(f"{message.author.mention}, your download of {p['title']} is here.", file = discord.File(f"Books/{p['title'].replace('/', '_')}.epub"))
            await msg.edit(content = f"Your request of:\n{ficInfo}\nis available at:\nhttps://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{fileMsg.id}")
            await message.remove_reaction('👍', client.user)
            await message.add_reaction('✅')
    elif message.content.startswith('!lookup'):  
        query = message.content.split()[1]
        p = ec.reqJson(lookUpPrefix + query)
        if 'error' in p:
            await message.channel.send("Query returned with an error")
            return 
        ficInfo = ec.metaDataString(p)[0]
        msg = await message.channel.send(f"Lookup Result: \n{ficInfo}")
    else:
        threads = []
        results = []
        keys = list(dict.fromkeys(message.content.split()))
        for word in keys:
            if len(word) > 5:
                t = threading.Thread(target=queryWorker, args=(lookUpPrefix + word, results))
                threads.append(t)
                t.start()
        for thread in threads:
            thread.join()
        if results == []:
            #msg = await client.send("Rawr X3 *nuzzles* How are you? *pounces on you* you're so warm o3o *notices you have a bulge* someone's happy! *nuzzles your necky wecky* ~murr~ hehe ;) *rubbies your bulgy wolgy* you're so big! *rubbies more on your bulgy wolgy* it doesn't stop growing .///. *kisses you and licks your neck* daddy likes ;) *nuzzle wuzzle* I hope daddy likes *wiggles butt and squirms* I wanna see your big daddy meat! *wiggles butt* I have a little itch o3o *wags tails* can you please get my itch? *put paws on your chest* nyea~ it's a seven inch itch *rubs your chest* can you pwease? *squirms* pwetty pwease? :( I need to be punished *runs paws down your chest and bites lip* like, I need to be punished really good *paws on your bulge as I lick my lips* I'm getting thirsty. I could go for some milk *unbuttons your pants as my eyes glow* you smell so musky ;) *licks shaft* mmmmmmmmmmmmmmmmmmm so musky ;) *drools all over your cawk* your daddy meat. I like. Mister fuzzy balls. *puts snout on balls and inhales deeply* oh my gawd. I'm so hard *rubbies your bulgy wolgy* *licks balls* punish me daddy nyea~ *squirms more and wiggles butt* I9/11 lovewas an yourinside muskyjob goodness *bites lip* please punish me *licks lips* nyea~ *suckles on your tip* so good *licks pre off your cock* salty goodness~ *eyes roll back and goes balls deep*, oh and also, Query returned with an error")
            return
        response = "Lookup Result:"
        results = list(dict.fromkeys(results))
        for result in results:
            response += "\n" + result
        msg = await message.channel.send(response)
                


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
client.run(TOKEN)