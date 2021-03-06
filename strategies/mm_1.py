#!/bin/usr/env python3
# -*- coding:utf-8 -*-
__author__ = 'Leo Tao'
# ===============================================================================
# LIBRARIES
# ===============================================================================
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Binance.client import Client
import configparser
import os
import time
from Binance.websockets import BinanceSocketManager
import json
import threading
import numpy as np
# ===============================================================================
# ===============================================================================


class binance_wrapper(BinanceSocketManager):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'.') + '/apiKey.ini')
        api_key = config.get('binance_03','api_key')
        api_secret = config.get('binance_03','api_secret')

        client = Client(api_key, api_secret)
        BinanceSocketManager.__init__(self,client)
        self.trade_count = 0
        self.processing_order = False
        self.locker = threading.Lock()

    def process_depth_message(self,msg):
        msg['TS'] = time.strftime('%Y-%m-%d %T')
        j_str = json.dumps(msg) + '\n'
        open(self.trade_symbol+'depth.p','a').write(j_str)

        _bid = round(float(msg['bids'][self.trade_depth][0]) * 1.00001,6)
        _ask = round(float(msg['asks'][self.trade_depth][0]) * 0.99999,6)
        fee = _bid*0.0005 + _ask*0.0005


        profit = _ask - _bid + 0.0000000001

        print(time.strftime('%Y-%m-%d %T'),'XXXXX++> bid : %s,ask : %s, cost/profit : %s, profit : %s ETH'%
              (_bid,_ask, fee/profit,( profit - fee )*88))
        if profit != 0:
            if fee / profit < self.trade_margin and self.processing_order is False:
                dic = {
                    'bid':_bid,
                    'ask':_ask,
                    'fee':fee,
                    'profit':profit
                }
                t = threading.Thread(target=self._process_my_order,kwargs = dic)
                t.start()


    def process_trade_message(self,msg):
        msg['TS'] = time.strftime('%Y-%m-%d %T')
        j_str = json.dumps(msg) + '\n'
        open(self.trade_symbol+'tradeRecord', 'a').write(j_str)


    def _process_my_order(self,bid, ask, fee, profit):
        print('processing order .........')
        self.processing_order = True
        time.sleep(2)
        my_orders = self._client.get_open_orders()
        my_orders_len = len([i['side'] for i in my_orders if i['symbol'] == self.trade_symbol])
        time.sleep(1)
        number_of_one_side_order = abs(
            len([i['side'] for i in my_orders if i['side'] == 'SELL' and i['symbol'] == self.trade_symbol]) - \
            len([i['side'] for i in my_orders if i['side'] == 'BUY' and i['symbol'] == self.trade_symbol]))
        print('total order : %s, on side order : %s'%(my_orders_len,number_of_one_side_order))
        if number_of_one_side_order < self.trade_numOrder and my_orders_len < self.trade_numOrder*2:
            self.trade_count += 1
            self._client.order_limit_buy(symbol=self.trade_symbol, quantity=self.trade_quantity, price=str(bid))
            self._client.order_limit_sell(symbol=self.trade_symbol, quantity=self.trade_quantity, price=str(ask))
            print(time.strftime('%Y-%m-%d %T'),
                  'trade %s ++> SET =====> |||| bid : %s,ask : %s, fees : %s, profit : %s ||||' % (self.trade_count
                                                                                                   , bid, ask,
                                                                                                   fee * self.trade_quantity,
                                                                                                   self.trade_quantity * (
                                                                                                   profit - fee)))
        time.sleep(60*np.e*my_orders_len/1.5+60)
        self.processing_order = False


    def start_depth(self, symbol,quantity,margin,orderDepth,numOrder):
        self.trade_quantity = quantity
        self.trade_margin = margin
        self.trade_depth = orderDepth
        self.trade_symbol = symbol
        self.trade_numOrder = numOrder
        self.start_depth_socket(symbol,self.process_depth_message,'20')

    def start_trade(self, symbol):
        self.start_trade_socket(symbol, self.process_trade_message)


def read_data():
    for i in open('depth.p','r').readlines():
        a = json.loads(i)
        print(a['TS'])


def trade():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__)) + '/apiKey.ini')
    api_key = config.get('binance_02', 'api_key')
    api_secret = config.get('binance_02', 'api_secret')
    client = Client(api_key, api_secret)
    #client.order_limit_sell(symbol = 'LOOMETH',quantity = 8, price ='0.00088180')
    a = client.get_open_orders()
    print(a)


if __name__ == '__main__':
    s = binance_wrapper()
    # s.start_trade('ZRXETH')
    # s.start_depth('ZRXETH',100,0.35,0,4)
    s.start_trade('LOOMETH')
    s.start_depth('LOOMETH', 300, 0.3, 0, 3)
    # s.start_trade('CMTETH')
    # s.start_depth('CMTETH', 300, 0.3, 0, 4)
    s.run()
    # trade()
