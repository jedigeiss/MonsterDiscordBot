#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 13:04:42 2018

@author: jan
"""
import sqlite3
#import sys
import datetime
import time
#import json
import locale
import requests
#from timeit import default_timer as timer
#import asyncio
from beem.blockchain import Blockchain
from pytz import timezone


locale.setlocale(locale.LC_ALL, '')

__url__ = 'https://steemmonsters.com/'
price_dict = {}


#db = sqlite3.connect("/home/ubuntu/bots/monsters/monster.db",
#                     detect_types=sqlite3.PARSE_DECLTYPES)

# The program is searching within the same folder for the DB
db = sqlite3.connect("monster.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)

cursor = db.cursor()
b = Blockchain()



def calculate_cooldown(played_block):
    block = b.get_current_block()
    block_number = block.block_num
    last_played = block_number - played_block
    #print(last_played, block_number, played_block)
    #print("difference in blocks", last_played)
    return last_played


def get_player_pic(player):
    newresponse = ""
    newresponse = requests.get("https://steemitimages.com/u/"+player+"/avatar")
    pic_url = newresponse.url
    return pic_url

def getplayer(player):
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "players/details?name=%s" % player)
        cnt2 += 1
    pic_url = get_player_pic(player)
    return response.json(), pic_url


def getquest(player):
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "players/quests?username=%s" % player)
        cnt2 += 1
    return response.json()

# currently not used, provides information about card stats like how
# many cards are available and so on
def getcardsstats():
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "cards/stats")
        if str(response) != '<Response [200]>':
            time.sleep(2)
        cnt2 += 1
    return response.json()


def do_add_tournament(name, price, date, link):
    datarow = (name, price, date, link)
    cursor.execute("INSERT INTO tournament(name, price, date, link)"
                   "VALUES(?,?,?,?)", datarow)
    db.commit()

    return 1

def get_tournament(anzahl):
    today = datetime.datetime.today()
    cursor.execute("SELECT * FROM tournament WHERE date > (?) ORDER BY"
                   " date(\"datum\") ASC LIMIT (?)", (today, anzahl, ))
    result = cursor.fetchall()
    if not result:
        return -1
    return result

def do_delete_tournament(key):
    try:
        cursor.execute("SELECT count(*) from tournament where id = ?", (key, ))
        result = cursor.fetchone()
        if result[0] == 1:
            cursor.execute("DELETE FROM tournament where id = ?", (key, ))
            db.commit()
            return 1
        return 0
    except sqlite3.Error as err:
        print(err)
        return -1

def get_league(rating):
    league = ""
    if 0 <= rating <= 99:
        league = "Novice"
    elif 100 <= rating <= 399:
        league = "Bronze III"
    elif 400 <= rating <= 699:
        league = "Bronze II"
    elif 700 <= rating <= 999:
        league = "Bronze I"
    elif 1000 <= rating <= 1299:
        league = "Silver III"
    elif 1300 <= rating <= 1599:
        league = "Silver II"
    elif 1600 <= rating <= 1899:
        league = "Silver I"
    elif 1900 <= rating <= 2199:
        league = "Gold III"
    elif 2200 <= rating <= 2499:
        league = "Gold II"
    elif 2500 <= rating <= 2799:
        league = "Gold I"
    elif 2800 <= rating <= 3099:
        league = "Diamond III"
    elif 3100 <= rating <= 3399:
        league = "Diamond II"
    elif 3400 <= rating <= 3699:
        league = "Diamond I"
    elif 3700 <= rating <= 4199:
        league = "Champion III"
    elif 4200 <= rating <= 4699:
        league = "Champion II"
    elif rating >= 4700:
        league = "Champion I"
    return league


def get_leaderboard():
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "players/leaderboard")
        if str(response) != '<Response [200]>':
            time.sleep(2)
        cnt2 += 1
    return response.json()


def get_card_price(card):
    #selection of minimal price per single card
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? "
                   "AND edition = ? ORDER BY buy_price ASC", (card, 0,))
    min_price_common_alpha = cursor.fetchone()
    if min_price_common_alpha is None:
        min_price_common_alpha = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? "
                   " AND edition = ? ORDER BY buy_price ASC", (card, 1,))
    min_price_common_beta = cursor.fetchone()
    if min_price_common_beta is None:
        min_price_common_beta = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? ORDER BY buy_price ASC", (card, 2,))
    min_price_common_promo = cursor.fetchone()
    if min_price_common_promo is None:
        min_price_common_promo = "-"

    #gold single cards
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card, 0, 1,))
    min_price_gold_alpha = cursor.fetchone()
    if min_price_gold_alpha is None:
        min_price_gold_alpha = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card, 1, 1,))
    min_price_gold_beta = cursor.fetchone()
    if min_price_gold_beta is None:
        min_price_gold_beta = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card, 2, 1,))
    min_price_gold_promo = cursor.fetchone()
    if min_price_gold_promo is None:
        min_price_gold_promo = "-"



    # selection of minimal price per bcx (from leveld cards)
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 0,))
    min_bcx_common_alpha = cursor.fetchone()
    if min_bcx_common_alpha is None:
        min_bcx_common_alpha = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 1,))
    min_bcx_common_beta = cursor.fetchone()
    if min_bcx_common_beta is None:
        min_bcx_common_beta = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 2,))
    min_bcx_common_promo = cursor.fetchone()
    if min_bcx_common_promo is None:
        min_bcx_common_promo = "-"

    # selection of minimal bcx from gold cards
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 0, 1,))
    min_bcx_gold_alpha = cursor.fetchone()
    if min_bcx_gold_alpha is None:
        min_bcx_gold_alpha = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 1, 1,))
    min_bcx_gold_beta = cursor.fetchone()
    if min_bcx_gold_beta is None:
        min_bcx_gold_beta = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 2, 1,))
    min_bcx_gold_promo = cursor.fetchone()
    if min_bcx_gold_promo is None:
        min_bcx_gold_promo = "-"


    #reward cards
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card, 3, 0,))
    min_price_common_reward = cursor.fetchone()
    if min_price_common_reward is None:
        min_price_common_reward = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 3, 0,))
    min_bcx_common_reward = cursor.fetchone()
    if min_bcx_common_reward is None:
        min_bcx_common_reward = "-"

    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card, 3, 1,))
    min_price_gold_reward = cursor.fetchone()
    if min_price_gold_reward is None:
        min_price_gold_reward = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card, 3, 1,))
    min_bcx_gold_reward = cursor.fetchone()
    if min_bcx_gold_reward is None:
        min_bcx_gold_reward = "-"



    return [min_price_common_alpha[0], min_price_common_beta[0],
            min_price_gold_alpha[0], min_price_gold_beta[0], min_bcx_common_alpha[0],
            min_bcx_common_beta[0], min_bcx_gold_alpha[0], min_bcx_gold_beta[0],
            min_price_common_promo[0], min_bcx_common_promo[0], min_price_gold_promo[0], min_bcx_gold_promo[0],
            min_price_common_reward[0], min_bcx_common_reward[0], min_price_gold_reward[0], min_bcx_gold_reward[0]]



def get_card_details():
    response = ""
    cnt2 = 0
    count = 0
    while str(response) != '<Response [200]>' and cnt2 < 15:
        response = requests.get(__url__ + "cards/get_details")
        if str(response) != '<Response [200]>':
            time.sleep(1)
        cnt2 += 1
    for r in response.json():
        c_id = r["id"]
        name = r["name"]
        name = name.lower()
        color = r["color"]
        typ = r["type"]
        rarity = r["rarity"]

        datarow = (c_id, name, color, typ, rarity)
        count += 1

        #datarow = (ort, planer, permlink, datum, uhrzeit)
        cursor.execute("INSERT INTO card(id, name, color, type, rarity)"
                       "VALUES(?,?,?,?,?)", datarow)
    db.commit()


def get_card_id(card_name):
    cursor.execute("SELECT id, url FROM card WHERE name = ?", (card_name,))
    c_id = cursor.fetchone()
    if c_id is None:
        return -1, 0
    return c_id[0], c_id[1]

def get_name_by_id(card_detail_id):
    cursor.execute("SELECT name FROM card WHERE id = ?", (card_detail_id,))
    name = cursor.fetchone()
    if name is None:
        return -1
    return name[0]


def get_rarity(c_id):
    cursor.execute("SELECT rarity FROM card WHERE id = ?", (c_id,))
    rarity = cursor.fetchone()
    if rarity is None:
        return -1
    return rarity[0]

def update_bcx(bcx_price, market_id):
    cursor.execute("UPDATE market SET bcx_price = ? where market_id = ?",
                   (round(bcx_price, 3), market_id,))


def get_single_cards(card_detail_id, edition, gold, xp):
    cards = 0
    rarity = get_rarity(card_detail_id)
    # Alpha Edition Cards per XP
    if edition == 0 and gold == 0 and rarity == 4:
        cards = (xp / 1000) +1
        #current_level = calculate_level()
    if edition == 0 and gold == 0 and rarity == 3:
        cards = (xp / 250) +1
    if edition == 0 and gold == 0 and rarity == 2:
        cards = (xp / 100) +1
    if edition == 0 and gold == 0 and rarity == 1:
        cards = (xp / 20) +1
    if edition == 0 and gold == 1 and rarity == 4:
        cards = xp / 2500
    if edition == 0 and gold == 1 and rarity == 3:
        cards = xp / 1000
    if edition == 0 and gold == 1 and rarity == 2:
        cards = xp / 500
    if edition == 0 and gold == 1 and rarity == 1:
        cards = xp / 250
    # Beta Edition Cards per XP
    if edition == 1 and gold == 0 and rarity == 4:
        cards = (xp / 750) +1
    if edition == 1 and gold == 0 and rarity == 3:
        cards = (xp / 175) +1
    if edition == 1 and gold == 0 and rarity == 2:
        cards = (xp / 75) +1
    if edition == 1 and gold == 0 and rarity == 1:
        cards = (xp / 15) +1
    if edition == 1 and gold == 1 and rarity == 4:
        cards = xp / 2000
    if edition == 1 and gold == 1 and rarity == 3:
        cards = xp / 800
    if edition == 1 and gold == 1 and rarity == 2:
        cards = xp / 400
    if edition == 1 and gold == 1 and rarity == 1:
        cards = xp / 200
    # Promo Edition Cards per XP
    if edition == 2 and gold == 0 and rarity == 4:
        cards = (xp / 1000) +1
    if edition == 2 and gold == 0 and rarity == 3:
        cards = (xp / 250) +1
    if edition == 2 and gold == 0 and rarity == 2:
        cards = (xp / 100) +1
    if edition == 2 and gold == 0 and rarity == 1:
        cards = (xp / 20) +1
    if edition == 2 and gold == 1 and rarity == 4:
        cards = xp / 2500
    if edition == 2 and gold == 1 and rarity == 3:
        cards = xp / 1000
    if edition == 2 and gold == 1 and rarity == 2:
        cards = xp / 500
    if edition == 2 and gold == 1 and rarity == 1:
        cards = xp / 250

    # Reward Edition Cards per XP
    if edition == 3 and gold == 0 and rarity == 4:
        cards = (xp / 750) +1
    if edition == 3 and gold == 0 and rarity == 3:
        cards = (xp / 175) +1
    if edition == 3 and gold == 0 and rarity == 2:
        cards = (xp / 75) +1
    if edition == 3 and gold == 0 and rarity == 1:
        cards = (xp / 15) +1
    if edition == 3 and gold == 1 and rarity == 4:
        cards = xp / 2000
    if edition == 3 and gold == 1 and rarity == 3:
        cards = xp / 800
    if edition == 3 and gold == 1 and rarity == 2:
        cards = xp / 400
    if edition == 3 and gold == 1 and rarity == 1:
        cards = xp / 200
    return cards

def get_card_worth(card_detail_id, edition, gold, xp):
    worth = 0
    if xp == 0:
        idstring = ("%s%s%s" % (card_detail_id, edition, gold))
        if idstring in price_dict:
            worth = price_dict[idstring]
            return worth
        cursor.execute("SELECT buy_price from market where card_detail_id = ? AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card_detail_id, edition, gold,))
        worth = cursor.fetchone()
        price_dict[idstring] = worth[0]
        return worth[0]
    else:
        cards = get_single_cards(card_detail_id, edition, gold, xp)

        if cards <= 1:
            idstring = ("%s%s%s" % (card_detail_id, edition, gold))
            if idstring in price_dict:
                worth = price_dict[idstring]
                return worth
            cursor.execute("SELECT buy_price from market where card_detail_id = ? AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card_detail_id, edition, gold,))
            worth = cursor.fetchone()
            price_dict[idstring] = worth[0]
            #print("einzelkarten mit xp", worth[0])
            return worth[0]
        elif cards > 1:
            idstring = ("%s%s%s" % (card_detail_id, edition, gold))
            if idstring in price_dict:
                worth = price_dict[idstring]
                worth = worth * cards
                return worth
            #print(card_detail_id, edition, gold, xp)
            cursor.execute("SELECT buy_price from market where card_detail_id = ? AND edition = ? AND gold = ? AND buy_price > 0 ORDER BY buy_price ASC", (card_detail_id, edition, gold,))
            bcx = cursor.fetchone()
            worth = cards * bcx[0]
            return worth

def get_player_cards(player):
    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 15:
        response = requests.get(__url__ + "cards/collection/" + player)
        if str(response) != '<Response [200]>':
            time.sleep(1)
        cnt2 += 1
    if "error" in response.json():
        return -1
    return response.json()


#def calculate_next_level(card_detail_id, edition, gold, cards):

def get_cards_on_cooldown(player):

    data = get_player_cards(player)
    for r in data["cards"]:
        cooldown = 0
#        minutes = 0
        card_detail_id = r["card_detail_id"]
#        edition = r["edition"]
        played_block = r["last_used_block"]
        if played_block is not None:
            cooldown = calculate_cooldown(int(played_block))
#            minutes = cooldown *3 / 60
            now = datetime.datetime.utcnow()
            now = now.replace(tzinfo=timezone('UTC'))
            now = now.astimezone(timezone('Europe/Berlin'))
            #print("now",now.strftime('%Y-%m-%d %H:%M:%S'))
            played_time = now.timestamp() - (cooldown*3)
            latestactivity = datetime.datetime.utcfromtimestamp(played_time)
            latestactivity = latestactivity.replace(tzinfo=timezone('UTC'))
            #value =datetime.datetime.strftime(played_time,"%d.%m.%Y %H:%M")
            latestactivity_cet = latestactivity.astimezone(timezone('Europe/Berlin'))
            cd_ends = latestactivity_cet + datetime.timedelta(days=7)

            print("Karte %s zuletzt gespielt:%s" % (card_detail_id, latestactivity_cet.strftime('%Y-%m-%d %H:%M:%S')))
            print("CD endet:%s " % cd_ends.strftime('%Y-%m-%d %H:%M:%S'))
            #print(card_detail_id,minutes, value)


            #print(card_detail_id,minutes)



def get_level_up(player):
    data = get_player_cards(player)
    for r in data["cards"]:
        xp = r["xp"]
        if xp == 0:
            print("nothing to do")
        elif xp > 0:
            card_detail_id = r["card_detail_id"]
            edition = r["edition"]
            gold = r["gold"]
            xp = r["xp"]
            print(card_detail_id)
            cards = get_single_cards(card_detail_id, edition, gold, xp)
            print("no cards", cards)
    return 0



def get_player_worth(player):
    worth = 0
    alpha = 0
    beta = 0
    promo = 0
    reward = 0
    gold_cards = 0
    valuable_card = {}
    valuable_card["worth"] = 0
    #return response.json()
    # get the profile image from steemit
    pic_url = get_player_pic(player)

    data = get_player_cards(player)
    for r in data["cards"]:
        card_detail_id = r["card_detail_id"]
        edition = r["edition"]
        # setting a few variables to do some statistics about the cards
        if edition == 0:
            alpha += 1
        elif edition == 1:
            beta += 1
        elif edition == 2:
            promo += 1
        elif edition == 3:
            reward += 1
        gold = r["gold"]
        if gold == 1:
            gold_cards += 1
            gold = 1
        elif gold == 0:
            gold = 0
        xp = r["xp"]

        #print(card_detail_id, edition, gold, xp)
        card_worth = get_card_worth(card_detail_id, edition, gold, xp)
        #card_worth = round(card_worth,3)
        # saving the most valuable card in a dict to access later on
        if card_worth > valuable_card["worth"]:
            valuable_card["worth"] = card_worth
            valuable_card["id"] = card_detail_id
            valuable_card["gold"] = gold
            valuable_card["xp"] = xp
            valuable_card["edition"] = edition

        #print("worth update card %s is worth %s" % (card_detail_id,card_worth) )
        worth += card_worth
    valuable_card["name"] = get_name_by_id(valuable_card["id"])
    worth = round(worth, 2)
    return [worth, alpha, beta, promo, reward, gold_cards, pic_url, valuable_card["name"], valuable_card["worth"]]

def calculate_bcx():
    cursor.execute("SELECT market_id, card_detail_id, buy_price, xp, edition, gold from market WHERE xp > 0")
    result = cursor.fetchall()
    for r in result:
        market_id = r[0]
        buy_price = r[2]
        c_id = r[1]
        edition = r[4]
        xp = r[3]
        gold = r[5]
        if gold == "1":
            gold = 1
        else:
            gold = 0
        # start of the classification of each card, in order to know how many single cards are merged.
        cards = get_single_cards(c_id, edition, gold, xp)
        bcx_price = buy_price / cards
        update_bcx(bcx_price, market_id)

    db.commit()

async def kill_price_dict():
    price_dict.clear()

def get_market_data():
    #clear database for the new snapshot
    #cursor.execute("DELETE FROM market")
    #db.commit()
    #price_dict.clear()

    response = ""
    cnt2 = 0
    count = 0
    while str(response) != '<Response [200]>' and cnt2 < 15:
        response = requests.get(__url__ + "market/for_sale")
        if str(response) != '<Response [200]>':
            time.sleep(1)
        cnt2 += 1

    cursor.execute("DELETE FROM market")
    db.commit()

    for r in response.json():
        market_id = r["market_id"]
        card_detail_id = r["card_detail_id"]
        edition = r["edition"]
        gold = r["gold"]
        uid = r["uid"]
        buy_price = r["buy_price"]
        seller = r["seller"]
        xp = r["xp"]

        datarow = (market_id, card_detail_id, edition, gold, uid, buy_price, seller, xp)
        count += 1

        #datarow = (ort, planer, permlink, datum, uhrzeit)
        cursor.execute("INSERT INTO market(market_id, card_detail_id, edition, gold, uid, buy_price, seller, xp)"
                       "VALUES(?,?,?,?,?,?,?,?)", datarow)
    db.commit()
    print("commit ausgführt")
    calculate_bcx()
