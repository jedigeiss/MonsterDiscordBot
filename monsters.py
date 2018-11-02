#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 13:04:42 2018

@author: jan
"""

import sys
from datetime import datetime, timedelta, date
import time
import json
import requests
from timeit import default_timer as timer
import sqlite3


__url__ = 'https://steemmonsters.com/'


db = sqlite3.connect("monster.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)
cursor = db.cursor()


def getplayer(player):
    response = ""
    cnt2 = 0
    
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "players/details?name=%s" % player)
        cnt2 += 1
    return response.json()


def getquest(player):
    response = ""
    cnt2 = 0
    
    while str(response) != '<Response [200]>' and cnt2 < 10:
        response = requests.get(__url__ + "players/quests?username=%s" % player)
        cnt2 += 1
    return response.json()
        

def getcardsstats(self):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "cards/stats")
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()
    

    
def get_card_price(card):
    
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? AND edition = ? ORDER BY buy_price ASC", (card,0,))
    min_price_common_alpha = cursor.fetchone()
    if min_price_common_alpha is None:
        min_price_common_alpha = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? AND edition = ? ORDER BY buy_price ASC", (card,1,))
    min_price_common_beta = cursor.fetchone()
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card,0,1,))
    min_price_gold_alpha = cursor.fetchone()
    if min_price_gold_alpha is None:
        min_price_gold_alpha = "-"
    cursor.execute("SELECT buy_price FROM market WHERE card_detail_id = ? AND edition = ? AND gold = ? ORDER BY buy_price ASC", (card,1,1,))
    min_price_gold_beta = cursor.fetchone()
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ? AND edition = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card,0,))
    min_bcx_common_alpha = cursor.fetchone()
    if min_bcx_common_alpha is None:
        min_bcx_common_alpha = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ? AND edition = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card,1,))
    min_bcx_common_beta = cursor.fetchone()
    if min_bcx_common_beta is None:
        min_bcx_common_beta = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ? AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card,0,1,))
    min_bcx_gold_alpha = cursor.fetchone()
    if min_bcx_gold_alpha is None:
        min_bcx_gold_alpha = "-"
    cursor.execute("SELECT bcx_price FROM market WHERE card_detail_id = ? AND edition = ? AND gold = ? AND bcx_price > 0 ORDER BY bcx_price ASC", (card,1,1,))
    min_bcx_gold_beta = cursor.fetchone()
    if min_bcx_gold_beta is None:
        min_bcx_gold_beta = "-"
    
    
    
    #min_price_common_beta =
    #min_price_gold_alpha = 
    #min_price_gold_beta = 
    
    
    return [min_price_common_alpha[0], min_price_common_beta[0],
            min_price_gold_alpha[0], min_price_gold_beta[0], min_bcx_common_alpha[0], min_bcx_common_beta[0], min_bcx_gold_alpha[0], min_bcx_gold_beta[0] ]
    

    
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
        count +=1
    
        #datarow = (ort, planer, permlink, datum, uhrzeit)
        cursor.execute("INSERT INTO card(id, name, color, type, rarity)"
                       "VALUES(?,?,?,?,?)", datarow)
    db.commit()
    
    
def get_card_id(card_name):
    cursor.execute("SELECT id, url FROM card WHERE name = ?", (card_name,))
    c_id = cursor.fetchone()
    if c_id is None:
        return -1, 0
    else:
        return c_id[0], c_id[1]

def get_rarity(c_id):
    cursor.execute("SELECT rarity FROM card WHERE id = ?", (c_id,))
    rarity = cursor.fetchone()
    if rarity is None:
        return -1
    else:
        return rarity[0]

def update_bcx(bcx_price,market_id):
    cursor.execute("UPDATE market SET bcx_price = ? where market_id = ?", (round(bcx_price, 3), market_id,))
            

def calculate_bcx():
    cursor.execute("SELECT market_id, card_detail_id, buy_price, xp, edition  from market WHERE xp > 0 AND gold == 0")
    result = cursor.fetchall()
    for r in result:
        market_id = r[0]
        buy_price = r[2]
        c_id = r[1]
        edition = r[4]
        xp = r[3]
        rarity = get_rarity(c_id)
        # start of the classification of each card, in order to know how many single cards are merged.
        if rarity == 4 and edition == 0:
            cards = (xp / 1000) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)        
        if rarity == 4 and edition == 1:
            cards = (xp / 750) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 3 and edition == 0:
            cards = (xp / 250) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 3 and edition == 1:
            cards = (xp / 175) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 2 and edition == 0:
            cards = (xp / 100) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 2 and edition == 1:
            cards = (xp / 75) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 1 and edition == 0:
            cards = (xp / 20) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 1 and edition == 1:
            cards = (xp / 15) +1
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
    db.commit()
    
    # Calculation of the gold foil cards
    cursor.execute("SELECT market_id, card_detail_id, buy_price, xp, edition  from market WHERE xp > 0 AND gold == 1")
    result = cursor.fetchall()
    for r in result:
        market_id = r[0]
        buy_price = r[2]
        c_id = r[1]
        edition = r[4]
        xp = r[3]
        rarity = get_rarity(c_id)
        # start of the classification of each card, in order to know how many single cards are merged.
        if rarity == 4 and edition == 0:
            cards = (xp / 2500)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)        
        if rarity == 4 and edition == 1:
            cards = (xp / 2000)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 3 and edition == 0:
            cards = (xp / 1000)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 3 and edition == 1:
            cards = (xp / 800)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 2 and edition == 0:
            cards = (xp / 500)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 2 and edition == 1:
            cards = (xp / 400)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 1 and edition == 0:
            cards = (xp / 250)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
        if rarity == 1 and edition == 1:
            cards = (xp / 200)
            bcx_price = buy_price / cards
            update_bcx(bcx_price, market_id)
    db.commit()
    
async def get_market_data():
    #clear database for the new snapshot
    cursor.execute("DELETE FROM market")
    db.commit()
    response = ""
    cnt2 = 0
    count = 0
    while str(response) != '<Response [200]>' and cnt2 < 15:
        response = requests.get(__url__ + "market/for_sale")
        if str(response) != '<Response [200]>':
            time.sleep(1)
        cnt2 += 1
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
        count +=1
    
        #datarow = (ort, planer, permlink, datum, uhrzeit)
        cursor.execute("INSERT INTO market(market_id, card_detail_id, edition, gold, uid, buy_price, seller, xp)"
                       "VALUES(?,?,?,?,?,?,?,?)", datarow)
    db.commit()
    calculate_bcx()
    
    
        
