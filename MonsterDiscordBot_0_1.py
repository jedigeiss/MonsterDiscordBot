#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:49:19 2018

@author: jan
"""

import datetime
import locale
import discord
import asyncio
from beem.account import Account

from discord.ext.commands import Bot
from discord.ext import commands
from monsters import getplayer
from monsters import getquest
from monsters import get_card_price
from monsters import get_card_id
from monsters import get_market_data

BOT_PREFIX = "!"


TOKEN = "Your Token here!"

locale.setlocale(locale.LC_ALL, '')

client = Bot(command_prefix=BOT_PREFIX)



@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def on_command_error(error, ctx):
    await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen: %s" % error)


async def update_market():
    await client.wait_until_ready()
    while not client.is_closed:
        get_market_data()
        print("update ausgeführt")
        await asyncio.sleep(300)



@client.command(description="Steem Monster Infos",
                brief="Detaillierte Infos über Spieler in Steemmonsters",
                aliases=["Monster"])
async def monster(player):
    data = getplayer(player)
    if "error" in data:
        await client.say("Der Spieler %s wurde auf Steemmonsters nicht gefunden" % player)
    else:
        name = data["name"]
        rank = data["rank"]
        rating = data["rating"]
        max_rating = data["max_rating"]
        join_date = data["join_date"]
        length = len(join_date)
        join_date = join_date[0:length-5]
        join_date = join_date.replace("T", " ")
        join_date = datetime.datetime.strptime(join_date, "%Y-%m-%d %H:%M:%S")
        battles = data["battles"]
        wins = data["wins"]
       
        embed = discord.Embed(title="Spieler übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Rang", value="%s" % rank)
        embed.add_field(name="Wertung", value="%s" % rating)
        embed.add_field(name="Max Wertung", value="%s" % max_rating)
        embed.add_field(name="Kämpfe", value="%s" % battles)
        embed.add_field(name="Siege", value="%s" % wins) 
        embed.add_field(name="Angemeldet seit", value="%s" %
                        (datetime.datetime.strftime(join_date, "%d.%m.%Y")))
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)


@client.command(description="Steem Monster Kartenwert alle Werte",
                brief="Kartenwert",
                aliases=["Wert"])
async def wert(*args):
    
    card_name = "{}".format(" ".join(args))
    c_id, url = get_card_id(card_name.lower())
    if c_id == -1:
        await client.say("Das Monster %s wurde nicht gefunden" % card_name)
    else:
        data = get_card_price(c_id)
        min_price_common_alpha = data[0]
        min_price_common_beta = data[1]
        min_price_gold_alpha = data[2]
        min_price_gold_beta = data[3]
        min_bcx_common_alpha = data[4]
        min_bcx_common_beta = data[5]
        min_bcx_gold_alpha = data[6]
        min_bcx_gold_beta = data[7]
        picurl = url
        #creating the embed to send to discord with all informations
        embed = discord.Embed(title="Kartenwert Übersicht :", description=card_name, color=0x00ff00)
        embed.add_field(name="Alpha Common", value="%s / %s $" % (min_price_common_alpha, min(min_bcx_common_alpha,min_price_common_alpha)))
        embed.add_field(name="Beta Common", value="%s / %s $" % (min_price_common_beta, min(min_bcx_common_beta, min_price_common_beta)))
        embed.add_field(name="Alpha Gold", value="%s / %s $" % (min_price_gold_alpha, min(min_bcx_gold_alpha,min_price_gold_alpha)))
        embed.add_field(name="Beta Gold", value="%s / %s $" % (min_price_gold_beta, min(min_bcx_gold_beta,min_price_gold_beta)))
        embed.set_thumbnail(url=picurl)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)



@client.command(description="Steem Monster Quest Info",
                brief="Detaillierte Infos über Quests eines Spielers",
                aliases=["Quest"])
async def quest(player):
    data = getquest(player)
    if "error" in data:
        await client.say("Der Spieler %s wurde auf Steemmonsters nicht gefunden" % player)
    else:
        data = data[0]
        name = data["name"]
        items = data["total_items"]
        completed = int(data["completed_items"])
        rewardqty = int(data["reward_qty"])
        progress = completed / items * 100
        if data["claim_date"] is not None:
            claimed = "Ja"
            claim_date = data["claim_date"]
            length = len(claim_date)
            claim_date = claim_date[0:length-5]
            claim_date = claim_date.replace("T", " ")
            claim_date = datetime.datetime.strptime(claim_date, "%Y-%m-%d %H:%M:%S")
            next_date = claim_date + datetime.timedelta(days=1) + datetime.timedelta(hours=1)
            print(claim_date) 
            next_date_str = datetime.datetime.strftime(next_date, "%d.%m.%Y %H:%M:%S")
        else:
            claimed = "Nein"
            next_date_str ="Not Available"
        #finding out the splinter of the quest
        splinter = ""
        if name == "Pirate Attacks": 
            splinter = "Wasser"
        elif name == "Defend the Borders":
            splinter = "Leben"
        elif name == "Lyanna's Call":
            splinter = "Erde"
        elif name == "Stir the Volcano":
            splinter = "Feuer"
        elif name == "Rising Dead":
            splinter = "Tod"
        #creating the embed to broadcast to discord
        embed = discord.Embed(title="Quest Übersicht Spieler :", description=player, color=0x00ff00)
        embed.add_field(name="Name", value="%s" % name)
        embed.add_field(name="Splinter", value="%s" % splinter)     
        embed.add_field(name="Fortschritt", value="%d Prozent" % progress)
        embed.add_field(name="Belohnung", value="%s Booster" % rewardqty)
        embed.add_field(name="Belohnung abgeholt?", value="%s" % claimed)
        embed.add_field(name="Nächste Quest", value="%s" % next_date_str)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)

@client.command(description="MonsterBot Version",
                brief="Version des MonsterBots",
                aliases=["Version", "ver", "Ver"])
async def version():
    await client.say("MonsterBot Version 0.1, brought to you by jedigeiss"
                     "\nThanks to: Holger80")


client.loop.create_task(update_market())

client.run(TOKEN)
