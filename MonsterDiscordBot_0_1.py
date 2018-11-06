#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:49:19 2018

@author: jan
"""
import asyncio
import datetime
import locale
import discord

#from beem.account import Account

from discord.ext.commands import Bot
#from discord.ext import commands
from monsters import getplayer
from monsters import getquest
from monsters import get_card_price
from monsters import get_card_id
from monsters import get_market_data
from monsters import get_player_cards
from monsters import get_leaderboard
BOT_PREFIX = "!"

# live bot token
#TOKEN = "YourTokenHere"



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



@client.command(description="Steem Monster Infos über einen Spieler",
                brief="Detaillierte Infos über Spieler in Steemmonsters",
                aliases=["Monster"])
async def monster(player):
    data, picurl = getplayer(player)
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
        champion_points = data["champion_points"]

        embed = discord.Embed(title="Spieler übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Rang", value="%s" % rank)
        embed.add_field(name="Wertung", value="%s" % rating)
        embed.add_field(name="Max Wertung", value="%s" % max_rating)
        embed.add_field(name="Kämpfe", value="%s" % battles)
        embed.add_field(name="Siege", value="%s" % wins)
        embed.add_field(name="Champion Points", value="%s" % champion_points)

        embed.add_field(name="Angemeldet seit", value="%s" %
                        (datetime.datetime.strftime(join_date, "%d.%m.%Y")))
        embed.set_thumbnail(url=picurl)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)


@client.command(description="Top 10 Ansicht aktuelle Rangfolge",
                brief="Top 10 Spieler",
                aliases=["Leaderboard, Tabelle, tabelle"])
async def leaderboard():
    data = get_leaderboard()
    if "error" in data:
        await client.say("Leaderboard konnte nicht geladen werden")
    else:
        ranking = []

        for r in data:
            ranking.append(r["player"])
            ranking.append(r["rating"])
            ranking.append(r["rank"])

        embed = discord.Embed(title="Leaderboard :", description="Steemmonsters Top 10"
                              , color=0x00ff00)
        embed.add_field(name="Spieler", value="%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s"
                        % (ranking[0], ranking[3], ranking[6], ranking[9], ranking[12],
                           ranking[15], ranking[18], ranking[21], ranking[24], ranking[27]))
        embed.add_field(name="Wertung", value="%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s"
                        % (ranking[1], ranking[4], ranking[7], ranking[10], ranking[13],
                           ranking[16], ranking[19], ranking[22], ranking[25], ranking[28]))
        embed.add_field(name="Rang", value="%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s"
                        % (ranking[2], ranking[5], ranking[8], ranking[11], ranking[14],
                           ranking[17], ranking[20], ranking[23], ranking[26], ranking[29]))
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)

@client.command(description="Aktueller Wert einer Karte aus Steemmonsters",
                brief="Aktueller Wert einer Karte",
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
        min_price_common_promo = data[8]
        min_bcx_common_promo = data[9]
        min_price_gold_promo = data[10]
        min_bcx_gold_promo = data[11]
        picurl = url
        #creating the embed to send to discord with all informations
        embed = discord.Embed(title="Kartenwert Übersicht :", description=card_name, color=0x00ff00)
        embed.add_field(name="Alpha Common", value="%s $/ %s $" %
                        (min_price_common_alpha, min(min_bcx_common_alpha, min_price_common_alpha)))
        embed.add_field(name="Alpha Gold", value="%s $/ %s $" %
                        (min_price_gold_alpha, min(min_bcx_gold_alpha, min_price_gold_alpha)))
        embed.add_field(name="Beta Common", value="%s $/ %s $" %
                        (min_price_common_beta, min(min_bcx_common_beta, min_price_common_beta)))
        embed.add_field(name="Beta Gold", value="%s $/ %s $" %
                        (min_price_gold_beta, min(min_bcx_gold_beta, min_price_gold_beta)))
        embed.add_field(name="Promo Common", value="%s $/ %s $" %
                        (min_price_common_promo, min(min_bcx_common_promo, min_price_common_promo)))
        embed.add_field(name="Promo Gold", value="%s $/ %s $" %
                        (min_price_gold_promo, min(min_bcx_gold_promo, min_price_gold_promo)))

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
            next_date_str = datetime.datetime.strftime(next_date, "%d.%m.%Y %H:%M:%S")
        else:
            claimed = "Nein"
            next_date_str = "Not Available"
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


@client.command(description="Berechnung des Gesamtwertes der Karten eines Spielers",
                brief="Gesamtwert pro Spieler",
                aliases=["Gesamtwert, gw"])
async def gesamtwert(player):
    data = get_player_cards(player)
    if data[0] == -1:
        await client.say("Der Spieler %s wurde auf Steemmonsters nicht gefunden" %player)
    else:
        name = player
        worth = data[0]
        alpha_cards = data[1]
        beta_cards = data[2]
        promo_cards = data[3]
        gold_cards = data[4]
        pic_url = data[5]
        valuable_card_name = data[6]
        valuable_card_worth = round(data[7], 3)

        embed = discord.Embed(title="Spieler übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Gesamtwert", value="%s $" % worth)
        embed.add_field(name="Alpha Karten", value="%s" % alpha_cards)
        embed.add_field(name="Beta Karten", value="%s" % beta_cards)
        embed.add_field(name="Promo Karten", value="%s" % promo_cards)
        embed.add_field(name="Goldene Karten", value="%s" % gold_cards)
        embed.add_field(name="Wertvollste Karte", value="%s" % valuable_card_name)
        embed.add_field(name="Kartenwert", value="%s $" % valuable_card_worth)
        embed.set_thumbnail(url=pic_url)
        #embed.add_field(name="Angemeldet seit", value="%s" %
        #                (datetime.datetime.strftime(join_date, "%d.%m.%Y")))
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)


@client.command(description="MonsterBot Version",
                brief="Version des MonsterBots",
                aliases=["Version", "ver", "Ver"])
async def version():
    await client.say("MonsterBot Version 0.2, brought to you by jedigeiss"
                     "\nThanks to: Holger80")


client.loop.create_task(update_market())

client.run(TOKEN)
