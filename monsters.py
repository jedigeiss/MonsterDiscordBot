#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 13:04:42 2018

@author: jan
"""
import sqlite3
import datetime
import time
import locale
import requests
from pytz import timezone
from collections import OrderedDict


locale.setlocale(locale.LC_ALL, '')

__url__ = 'https://steemmonsters.com/'
price_dict = {}


db = sqlite3.connect("monster.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)


cursor = db.cursor()



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
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ? "
                   "AND edition = ?", (card, 0,))
    min_price_common_alpha = cursor.fetchone()
    if min_price_common_alpha is None:
        min_price_common_alpha = "-"
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ? "
                   " AND edition = ?", (card, 1,))
    min_price_common_beta = cursor.fetchone()
    if min_price_common_beta is None:
        min_price_common_beta = "-"
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ?", (card, 2,))
    min_price_common_promo = cursor.fetchone()
    if min_price_common_promo is None:
        min_price_common_promo = "-"

    #gold single cards
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 0, 1,))
    min_price_gold_alpha = cursor.fetchone()
    if min_price_gold_alpha is None:
        min_price_gold_alpha = "-"
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 1, 1,))
    min_price_gold_beta = cursor.fetchone()
    if min_price_gold_beta is None:
        min_price_gold_beta = "-"
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 2, 1,))
    min_price_gold_promo = cursor.fetchone()
    if min_price_gold_promo is None:
        min_price_gold_promo = "-"



    # selection of minimal price per bcx (from leveld cards)
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ?", (card, 0,))
    min_bcx_common_alpha = cursor.fetchone()
    if min_bcx_common_alpha is None:
        min_bcx_common_alpha = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ?", (card, 1,))
    min_bcx_common_beta = cursor.fetchone()
    if min_bcx_common_beta is None:
        min_bcx_common_beta = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ?", (card, 2,))
    min_bcx_common_promo = cursor.fetchone()
    if min_bcx_common_promo is None:
        min_bcx_common_promo = "-"

    # selection of minimal bcx from gold cards
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 0, 1,))
    min_bcx_gold_alpha = cursor.fetchone()
    if min_bcx_gold_alpha is None:
        min_bcx_gold_alpha = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 1, 1,))
    min_bcx_gold_beta = cursor.fetchone()
    if min_bcx_gold_beta is None:
        min_bcx_gold_beta = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 2, 1,))
    min_bcx_gold_promo = cursor.fetchone()
    if min_bcx_gold_promo is None:
        min_bcx_gold_promo = "-"


    #reward cards
    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 3, 0,))
    min_price_common_reward = cursor.fetchone()
    if min_price_common_reward is None:
        min_price_common_reward = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 3, 0,))
    min_bcx_common_reward = cursor.fetchone()
    if min_bcx_common_reward is None:
        min_bcx_common_reward = "-"

    cursor.execute("SELECT buy_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 3, 1,))
    min_price_gold_reward = cursor.fetchone()
    if min_price_gold_reward is None:
        min_price_gold_reward = "-"
    cursor.execute("SELECT bcx_price FROM newmarket WHERE card_detail_id = ?"
                   " AND edition = ? AND gold = ?", (card, 3, 1,))
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

    cursor.execute("SELECT id FROM card")
    all_ids = [item[0] for item in cursor.fetchall()]
    print(all_ids)

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
        pic_adress = name.title()
        pic_adress = pic_adress.replace(" ", "%20")
        pic_adress = "https://s3.amazonaws.com/steemmonsters/cards_untamed/" + pic_adress +".png"
        if c_id in all_ids:
            print("already there doing nothing")
        else:

            datarow = (c_id, name, color, typ, rarity, pic_adress)
            count += 1
            print(datarow)
            cursor.execute("INSERT INTO card(id, name, color, type, rarity, url)"
                           "VALUES(?,?,?,?,?,?)", datarow)
            db.commit()
    print("added %s cards" % count)



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
        
    # Untamed Edition Cards per XP    
    if edition == 4:
        cards = xp
    return cards

def get_card_worth(card_detail_id, edition, gold, xp):
    worth = 0
    bcx_flag = 0
    if xp == 0:
        idstring = ("%s%s%s%s" % (card_detail_id, edition, gold, bcx_flag))
        if idstring in price_dict:
            worth = price_dict[idstring]
            return worth
        cursor.execute("SELECT buy_price from newmarket where card_detail_id = ? AND edition = ? AND gold = ?", (card_detail_id, edition, gold,))
        worth = cursor.fetchone()
        price_dict[idstring] = worth[0]
        return worth[0]
    else:
        cards = get_single_cards(card_detail_id, edition, gold, xp)

        if cards <= 1:
            idstring = ("%s%s%s%s" % (card_detail_id, edition, gold, bcx_flag))
            if idstring in price_dict:
                worth = price_dict[idstring]
                return worth
            cursor.execute("SELECT buy_price from newmarket where card_detail_id = ? AND edition = ? AND gold = ?", (card_detail_id, edition, gold,))
            worth = cursor.fetchone()
            price_dict[idstring] = worth[0]
            return worth[0]
        elif cards > 1:
            bcx_flag = 1
            idstring = ("%s%s%s%s" % (card_detail_id, edition, gold, bcx_flag))
            if idstring in price_dict:
                worth = price_dict[idstring]
                worth = worth * cards
                return worth
            cursor.execute("SELECT bcx_price from newmarket where card_detail_id = ? AND edition = ? AND gold = ?", (card_detail_id, edition, gold,))
            bcx = cursor.fetchone()
            worth = cards * bcx[0]
            price_dict[idstring] = bcx[0]
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



def get_player_worth_leased(player):
    delegation_in_worth = 0
    delegation_out_worth = 0
    delegation_in_counter = 0
    delegation_out_counter = 0
    alpha = 0
    beta = 0
    promo = 0
    reward = 0
    gold_cards = 0
    top_cards_incoming = {}
    top_cards_outgoing = {}
    pic_url = get_player_pic(player)

    data = get_player_cards(player)
    for r in data["cards"]:
        delegated_in = False
        delegated_out = False
        card_detail_id = r["card_detail_id"]
        edition = r["edition"]
        # check the delegation status of the card
        if r["player"] != player:
            delegation_in_counter +=1
            delegated_in = True
        else:
            if r["delegated_to"] is not None:
                delegation_out_counter +=1
                delegated_out = True

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

        if delegated_out:
            card_worth = get_card_worth(card_detail_id, edition, gold, xp)
            name = get_name_by_id(card_detail_id)
            top_cards_outgoing[delegation_out_counter] = {"name": name.title(), "to" : r["delegated_to"], "worth" : card_worth}
            delegation_out_worth += card_worth

        elif delegated_in:
            card_worth = get_card_worth(card_detail_id, edition, gold, xp)
            name = get_name_by_id(card_detail_id)
            top_cards_incoming[delegation_in_counter] = {"name": name.title(), "from" : r["player"], "worth" : card_worth}
            delegation_in_worth += card_worth

    sortiert_out = OrderedDict(sorted(top_cards_outgoing.items(), key=lambda x: x[1]["worth"], reverse=True))
    firstthree_out = {k: sortiert_out[k] for k in list(sortiert_out)[:3]}
    sortiert_in = OrderedDict(sorted(top_cards_incoming.items(), key=lambda x: x[1]["worth"], reverse=True))
    firstthree_in = {k: sortiert_in[k] for k in list(sortiert_in)[:3]}
    return [firstthree_out, firstthree_in, round(delegation_out_worth,3), round(delegation_in_worth,3), pic_url]



def get_player_worth(player):
    delegation_in_worth = 0
    delegation_out_worth = 0
    delegation_in_counter = 0
    delegation_out_counter = 0
    worth = 0
    alpha = 0
    alpha_value = 0
    beta = 0
    beta_value = 0
    promo = 0
    promo_value = 0
    reward = 0
    reward_value = 0
    untamed = 0
    untamed_value = 0
    gold_cards = 0
    valuable_card = {}
    valuable_card["worth"] = 0
    # get the profile image from steemit
    pic_url = get_player_pic(player)

    data = get_player_cards(player)
    for r in data["cards"]:
        delegated_in = False
        delegated_out = False
        card_detail_id = r["card_detail_id"]
        edition = r["edition"]
        # check the delegation status of the card
        if r["player"] != player:
            delegation_in_counter +=1
            delegated_in = True
            #print(player, card_detail_id)
        else:
            if r["delegated_to"] is not None:
                delegation_out_counter +=1
                delegated_out = True
        # setting a few variables to do some statistics about the cards
        
        gold = r["gold"]
        if gold == 1:
            gold_cards += 1
            gold = 1
        elif gold == 0:
            gold = 0
        xp = r["xp"]

        card_worth = get_card_worth(card_detail_id, edition, gold, xp)
        # saving the most valuable card in a dict to access later on
        
        if edition == 0:
            alpha += 1
            alpha_value += card_worth
        elif edition == 1:
            beta += 1
            beta_value += card_worth
        elif edition == 2:
            promo += 1
            promo_value += card_worth
        elif edition == 3:
            reward += 1
            reward_value += card_worth
        elif edition == 4:
            untamed_value += card_worth
            untamed +=1
            
        if delegated_in is False and card_worth > valuable_card["worth"]:
            valuable_card["worth"] = card_worth
            valuable_card["id"] = card_detail_id
            valuable_card["gold"] = gold
            valuable_card["xp"] = xp
            valuable_card["edition"] = edition

        # calculcate the different types of worth, total value, delegation in and delegation out
        if delegated_in is False:
            worth += card_worth
            if delegated_out is True:
                delegation_out_worth += card_worth
        else:
            delegation_in_worth += card_worth

    valuable_card["name"] = get_name_by_id(valuable_card["id"])
    worth = round(worth, 2)
    delegation_in_worth = round(delegation_in_worth, 2)
    delegation_out_worth = round(delegation_out_worth, 2)
    #print(untamed, untamed_value)
    #print(alpha, alpha_value)
    #print(beta, beta_value)
    #print(reward, reward_value)
    #print(promo, promo_value)
    
    return [worth, alpha, beta, promo, reward, gold_cards, pic_url, valuable_card["name"], valuable_card["worth"], delegation_in_worth
            , delegation_out_worth, alpha_value, beta_value, promo_value, reward_value, untamed_value, untamed]

async def kill_price_dict():
    price_dict.clear()

def get_new_market_data():
    cursor.execute("DELETE FROM newmarket")
    db.commit()

    response = ""
    cnt2 = 0
    while str(response) != '<Response [200]>' and cnt2 < 15:
        response = requests.get(__url__ + "market/for_sale_grouped")
        if str(response) != '<Response [200]>':
            time.sleep(1)
        cnt2 += 1

    for r in response.json():
        card_detail_id = r["card_detail_id"]
        edition = r["edition"]
        gold = r["gold"]
        buy_price = round(r["low_price"], 3)
        bcx_price = round(r["low_price_bcx"], 3)
        datarow = (card_detail_id, edition, gold, buy_price, bcx_price)

        cursor.execute("INSERT INTO newmarket(card_detail_id, edition, gold, buy_price, bcx_price)"
                       "VALUES(?,?,?,?,?)", datarow)
    db.commit()
