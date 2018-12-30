#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:49:19 2018

@author: jan
This is version 0.2 of the MonsterBot


"""
import asyncio
import datetime
import locale
import discord

#from beem.account import Account

from discord.ext.commands import Bot
from discord.ext import commands
from monsters import getplayer
from monsters import getquest
from monsters import get_card_price
from monsters import get_card_id
#from monsters import get_market_data
from monsters import get_player_worth
from monsters import get_leaderboard
#from monsters import get_level_up
#from monsters import calculate_bcx
from monsters import kill_price_dict
from monsters import do_add_tournament
from monsters import get_tournament
from monsters import do_delete_tournament
from monsters import get_league

# This is the prefix that the bot listens to
BOT_PREFIX = "!"

# live bot token
TOKEN = "Put your token here"

#Testbot Token
#TOKEN = "if you have a testbot token you can put it here"


locale.setlocale(locale.LC_ALL, '')

client = Bot(command_prefix=BOT_PREFIX)



@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def on_command_error(error, ctx):
    await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen: %s" % error)


async def update_market():
    '''This function deletes the price_dict that stores all prices per card
    in RAM every 120 seconds.
    This is necessary because people tend to have a lot of cards in their
    set and loading the prices all out of the DB would take way to long.
    The dict gets deleted to be containing only the latest prices
    Arguments: None
    Returns: Nothing
    '''
    await client.wait_until_ready()
    while not client.is_closed:
        await kill_price_dict()
        await asyncio.sleep(120)



@client.command(description="Steem Monster Infos über einen Spieler",
                brief="Detaillierte Infos über Spieler in Steemmonsters",
                aliases=["Monster"])
async def monster(player):
    '''This function calls the getplayer function and displays all
    informations about a player in Discord
    Arguments: player name
    Returns: all informations displaed in Discord
    '''
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
        league = get_league(rating)


        embed = discord.Embed(title="Spieler übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Rang", value="%s" % rank)
        embed.add_field(name="Wertung", value="%s" % rating)
        embed.add_field(name="Liga", value="%s" % league)
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
                aliases=["Leaderboard", "Tabelle", "tabelle"])
async def leaderboard():
    '''Gets and displays the current leaderboard in Discord
    '''
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
    '''Gets the current prices for a single card and displays the info in
    a discord channel
    '''
    card_name = "{}".format(" ".join(args))
    card_name = card_name.title()
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
        min_price_common_reward = data[12]
        min_bcx_common_reward = data[13]
        min_price_gold_reward = data[14]
        min_bcx_gold_reward = data[15]


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
        embed.add_field(name="Reward Common", value="%s $/ %s $" %
                        (min_price_common_reward, min(min_bcx_common_reward, min_price_common_reward)))
        embed.add_field(name="Reward Gold", value="%s $/ %s $" %
                        (min_price_gold_reward, min(min_bcx_gold_reward, min_price_gold_reward)))


        embed.set_thumbnail(url=picurl)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)



@client.command(description="Steem Monster Quest Info",
                brief="Detaillierte Infos über Quests eines Spielers",
                aliases=["Quest"])
async def quest(player):
    '''Gets the current quest for a specific player and displays the related
    information in discord
    '''
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
                aliases=["Gesamtwert", "gw"])
async def gesamtwert(player):
    '''calculates the overall worth of all cards of a specific player and
    displays this information within a discord channel
    '''
    data = get_player_worth(player)
    if data[0] == -1:
        await client.say("Der Spieler %s wurde auf Steemmonsters nicht gefunden" %player)
    else:
        name = player
        worth = data[0]
        alpha_cards = data[1]
        beta_cards = data[2]
        promo_cards = data[3]
        reward_cards = data[4]
        gold_cards = data[5]
        pic_url = data[6]
        valuable_card_name = data[7]
        valuable_card_worth = round(data[8], 3)

        embed = discord.Embed(title="Spieler übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Gesamtwert", value="%s $" % worth)
        embed.add_field(name="Alpha Karten", value="%s" % alpha_cards)
        embed.add_field(name="Beta Karten", value="%s" % beta_cards)
        embed.add_field(name="Promo Karten", value="%s" % promo_cards)
        embed.add_field(name="Reward Karten", value="%s" % reward_cards)
        embed.add_field(name="Goldene Karten", value="%s" % gold_cards)
        embed.add_field(name="Wertvollste Karte", value="%s, %s $" % (valuable_card_name, valuable_card_worth))
        embed.set_thumbnail(url=pic_url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
        await client.say(embed=embed)


@client.command(description="Anlegen eines Steem Monster Turniers",
                brief="Anlegen eines Turniers",
                aliases=["add_t"])
@commands.has_role("Admin")
async def add_tournament(*args):
    message = "{}".format(" ".join(args))
    split = message.split(",")

    name = split[0]
    price = split[1][1:]
    date = split[2][1:]
    time = split[3][1:]
    link = split[4][1:]

    date = date + " " + time
    date = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M")
    result = do_add_tournament(name, price, date, link)
    if result == 1:
        await client.say("Neues Turnier: %s erfolgreich hinzugefügt" % name)

@client.command(description="Löschen eines Steem Monster Turniers",
                brief="Löschen eines Turniers",
                aliases=["del_t"])
@commands.has_role("Admin")
async def del_tournament(key):
    result = do_delete_tournament(key)
    if result == 1:
        await client.say("Turnier mit ID %s erfolgreich gelöscht" % key)
    if result == 0:
        await client.say("Turnier mit ID %s konnte nicht gefunden werden" % key)




@client.command(description="Anzeigen der nächsten Steem Monster Turniere",
                brief="Anzeigen der Turniere",
                aliases=["turniere", "Turniere"])
async def show_tournament(anzahl=4):
    result = get_tournament(anzahl)
    #today = datetime.datetime.today()
    if result == -1:
        await client.say("Keine zukünftigen"
                         " Turniere in der Datenbank gefunden")

    else:
        for r in result:
            embed = discord.Embed(title="Turnier: %s" % r[1], description="", color=0x00ff00)
            embed.add_field(name="Preisgeld", value="%s" % r[2])
            embed.add_field(name="Datum", value="%s" % datetime.datetime.strftime(r[3], "%d.%m.%Y"), inline=True)
            embed.add_field(name="Uhrzeit", value="%s Uhr" % datetime.datetime.strftime(r[3], "%H:%M"), inline=True)
            embed.add_field(name="Link", value="[Link zum Turnier](%s) " % str(r[4]), inline=True)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="ID: %s | fresh from the MonsterBot" % r[0])
            await client.say(embed=embed)


# =============================================================================
# @client.command(description="Anzeige der einfachsten Levelup Möglichkeiten pro Spieler",
#                 brief="Einfache Levelups",
#                 aliases=["Levelup, level"])
# async def levelup(player):
#     data = get_level_up(player)
#     if data[0] == -1:
#         await client.say("Der Spieler %s wurde auf Steemmonsters nicht gefunden" %player)
#     else:
#         name = player
#         worth = data[0]
#         alpha_cards = data[1]
#         beta_cards = data[2]
#         promo_cards = data[3]
#         gold_cards = data[4]
#         pic_url = data[5]
#         valuable_card_name = data[6]
#         valuable_card_worth = round(data[7], 3)
#
#         embed = discord.Embed(title="Top 5 Level up Übersicht :", description=player, color=0x00ff00)
#         embed.add_field(name="Gesamtwert", value="%s $" % worth)
#         embed.add_field(name="Alpha Karten", value="%s" % alpha_cards)
#         embed.add_field(name="Beta Karten", value="%s" % beta_cards)
#         embed.add_field(name="Promo Karten", value="%s" % promo_cards)
#         embed.add_field(name="Goldene Karten", value="%s" % gold_cards)
#         embed.add_field(name="Wertvollste Karte", value="%s" % valuable_card_name)
#         embed.add_field(name="Kartenwert", value="%s $" % valuable_card_worth)
#         embed.set_thumbnail(url=pic_url)
#         embed.timestamp = datetime.datetime.utcnow()
#         embed.set_footer(text="fresh from the MonsterBot and Steemmonsters")
#         await client.say(embed=embed)
#
# =============================================================================



@client.command(description="MonsterBot Version",
                brief="Version des MonsterBots",
                aliases=["Version", "ver", "Ver"])
async def version():
    '''puts the current version of the MonsterBot
    '''
    await client.say("MonsterBot Version 0.2, brought to you by jedigeiss"
                     "\nThanks to: Holger80 and Rivalzzz")


client.loop.create_task(update_market())

client.run(TOKEN)
