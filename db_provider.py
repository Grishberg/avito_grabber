#!/usr/bin/python
# -*- coding: utf-8

import json
import MySQLdb
import sys, traceback
import response_fields as rf
from config import *
from Apartment import *


# Класс работы с бд
class DbService:
    def __init__(self):
        # подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
        self.db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
        # формируем курсор, с помощью которого можно исполнять SQL-запросы
        self.cursor = self.db.cursor()

    # закрываем соединение с базой данных
    def close(self):
        try:
            self.db.close()
        except Exception as e:
            print e

    def get_connection(self):
        self.db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
        self.cursor = self.db.cursor()
        return self.db

    def store_to_db(self, list_data):
        pass

    # API
    def get_ads(self):
        sql = "SELECT url, title, address, metro, metro_distance, price, pos_l, pos_w, date"
        sql += " FROM apartments ORDER BY date DESC;"
        data = []
        result = []
        try:
            # Execute the SQL command
            self.cursor.execute(sql, data)
            # Fetch all the rows in a list of lists.
            rows = self.cursor.fetchall()
            for row in rows:
                result.append(Apartment({rf.URL: row[0], rf.TITLE: row[1], rf.ADDRESS: row[2],
                                         rf.METRO: row[3], rf.METRO_DISTANCE: row[4],
                                         rf.PRICE: row[5], rf.POS_L: row[6], rf.POS_W: row[7],
                                         rf.DATE: row[8]}))
            return result
        except Exception as e:
            print ("Error: unable to fecth data, " + str(e))
            return None
        finally:
            self.close()


            # services list for client

    def add_ads(self, ads_list):
        self.get_connection()
        added_count = 0
        for item in ads_list:
            ad = item.data
            sql = ("INSERT INTO apartments "
                   "(url, title, address, metro, metro_distance, price, pos_l, pos_w, date) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
            data = (ad[rf.URL], ad[rf.TITLE], ad[rf.ADDRESS], ad[rf.METRO], ad[rf.METRO_DISTANCE],
                    ad[rf.PRICE], ad[rf.POS_L], ad[rf.POS_W], ad[rf.DATE])
            try:
                # Execute the SQL command
                self.cursor.execute(sql, data)
                result_id = self.cursor.lastrowid
                self.db.commit()
                added_count += 1

            except Exception as e:
                self.db.rollback()
                print ("Error: unable to insert data, " + str(e))

        self.close()
        return added_count

    def clear(self):
        pass
