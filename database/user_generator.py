#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import string
import random
import pandas as pd
from cassandra.cluster import Cluster
# 'This scipt will create a list of user with
# username, stock,Current holding value,# stock, buy,sell amount'


def name_generator():
    """
    Returns a randomized username thorugh a combination of
    number and strings in length of 7
    
    Inputs:  None
    @rtype:  string
    @return: randomized username
    """
    length = 7
    res = ''.join(random.choices(string.ascii_uppercase
                                 + string.digits, k=length))
    return res


def stock_generator(data):
    """
    open a documnet of historical data from NYSE and randomly generate a
    stock ticker through randomly selecting in file
    
    @type  data:  dataframe
    @param data: A historical file of stock data
    @rtype:      string
    """
    ticker = data[1]
    return ticker[random.randint(1, 15796358)]


def main(num):
    """
    generate a selected amount of user data and writes it to cassandra
    database. There is no reason and only takes on input, numbers. it calls
    stock_generator which generate user selected ticker and name_generator
    which generates the name. Inside the main, parameters suc as buy,sell
    and cash will be randomized.
    
    @type  num: number
    @param num: number of users to generate
    """
    data = pd.read_csv('<TAQFileDirectory>', header=None, low_memory=False)
    cluster = Cluster(["<cluster-IP>"])
    session = cluster.connect('users')
    for i in range(num):
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
    num = 10000
    main(num)
