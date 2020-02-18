#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
import random
import pandas as pd
from cassandra.cluster import Cluster
# 'This scipt will create a list of user with
# username, stock,Current holding value,# stock, buy,sell amount'


def name_generator():
    length = 7
    res = ''.join(random.choices(string.ascii_uppercase
                                 + string.digits, k=length))
    return res


def stock_generator(data):
    # 'open a day trading data,randomly select an interger
    # from 1 to 15796358(len(file))
    # pull the ticker of random interger on csv file'
    ticker = data[1]
    return ticker[random.randint(1, 15796358)]


def main():
    # generate users data
    data = pd.read_csv('<TAQFileDirectory>', header=None, low_memory=False)
    cluster = Cluster(["<cluster-IP>"])
    session = cluster.connect('users')
    for i in range(100000):
        user = name_generator()
        ticker = stock_generator(data)
        session.execute("""insert into users.user_data(time,user,ticker,
                        numb_share,profit,buy,sell,previous_price,total_value,
                        cash) values (%(time)s,%(user)s,%(ticker)s,
                        %(numb_share)s,%(profit)s,%(buy)s,%(sell)s,
                        %(previous_price)s,%(total_value)s,%(cash)s)""",
                        {'time': 0, 'user': user, 'ticker': ticker,
                         'numb_share': 0, 'profit': 0, 'buy': random.randint(10, 40)/100,
                         'sell': random.randint(5, 40)/100, 'previous_price': 0,
                         'total_value': 0, 'cash': random.randint(2000, 400000)})
        session.execute("""insert into users.directory_data(user,ticker)
                   values (%(user)s,%(ticker)s)""", {'user': user, 'ticker': ticker})


if __name__ == '__main__':
    main()
