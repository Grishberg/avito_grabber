#!/usr/bin/python
# -*- coding: utf-8

import MySQLdb
import sys, traceback
import response_fields as rf
from config import *
from Apartment import *
from range_chacker import Point


# Класс работы с бд
class DbService:
    def __init__(self):
        self._closed = True
        # подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
        self.db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
        # формируем курсор, с помощью которого можно исполнять SQL-запросы
        self.cursor = self.db.cursor()

    # закрываем соединение с базой данных
    def close(self):
        if self._closed:
            return
        try:
            self.db.close()
            self._closed = True
        except Exception as e:
            print e

    def get_connection(self):
        if self._closed:
            self.db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
            self.cursor = self.db.cursor()
            self._closed = False
        return self.db

    # API
    def get_ads(self):
        self.get_connection()
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
            error_str = str(e)
            print ("Error: unable to fecth data, " + error_str)
            return None
        finally:
            self.close()


            # services list for client

    def add_ads(self, ads_list):
        self.get_connection()
        ids = []
        for item in ads_list:
            ad = item.data
            sql = ("INSERT INTO apartments "
                   "(url, photo, title, address, metro, metro_distance, price, fee, pos_l, pos_w, date) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            data = (ad[rf.URL], ad[rf.PHOTO], ad[rf.TITLE], ad[rf.ADDRESS], ad[rf.METRO], ad[rf.METRO_DISTANCE],
                    ad[rf.PRICE], ad[rf.PRICE_FEE], ad[rf.POS_L], ad[rf.POS_W], ad[rf.DATE])
            try:
                # Execute the SQL command
                self.cursor.execute(sql, data)
                ids.append(self.cursor.lastrowid)
                self.db.commit()

            except Exception as e:
                self.db.rollback()
                error_str = str(e)
                if error_str.find("duplicate") > 0:
                    self.udpate_apartment_by_url(ad[rf.URL], ad[rf.DATE])
                print ("Error: unable to insert data, " + error_str)

        self.close()
        return ids

    def clear(self):
        pass

    def udpate_apartment_by_url(self, url, date):
        update_sql = "UPDATE apartments SET date = %s WHERE url = %s"
        update_data = (date, url)
        try:
            # Execute the SQL command
            self.cursor.execute(update_sql, update_data)
            self.db.commit()
            return self.get_id_by_url(url)
        except Exception as e:
            self.db.rollback()
            error_str = str(e)
            print ("Error: unable to insert data, " + error_str)

    def get_id_by_url(self, url):
        sql = "SELECT id FROM apartments WHERE url = %s"
        data = (url)
        try:
            # Execute the SQL command
            self.cursor.execute(sql, data)
            # Fetch all the rows in a list of lists.
            rows = self.cursor.fetchall()
            for row in rows:
                return row[0]

        except Exception as e:
            self.db.rollback()
            error_str = str(e)
            print ("Error: unable to insert data, " + error_str)

    # points as list of Point
    def add_circuit(self, user_id, points):
        self.get_connection()
        circuit_id = self._add_circuit(user_id)
        if circuit_id == 0:
            return None
        id = 0
        for point in points:
            sql = ("INSERT INTO points "
                   "(circuits_id, pos_w, pos_l) "
                   "VALUES (%s, %s, %s)")
            data = (circuit_id, point.x, point.y)
            try:
                # Execute the SQL command
                self.cursor.execute(sql, data)
                id = self.cursor.lastrowid
                self.db.commit()

            except Exception as e:
                self.db.rollback()
                error_str = str(e)

                print ("Error: unable to insert data, " + error_str)

        self.close()
        return id

    def _add_circuit(self, user_id):
        id = 0

        sql = ("INSERT INTO circuits "
               "(user_id) "
               "VALUES (%s)")
        data = [user_id]
        try:
            # Execute the SQL command
            self.cursor.execute(sql, data)
            id = self.cursor.lastrowid
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            error_str = str(e)
            print ("Error: unable to insert data, " + error_str)
        return id

    def get_circuits(self, user_id):
        self.get_connection()
        sql = "SELECT id FROM circuits WHERE user_id = %s;"
        data = [user_id]
        ids = []
        try:
            # Execute the SQL command
            self.cursor.execute(sql, data)
            # Fetch all the rows in a list of lists.
            rows = self.cursor.fetchall()
            for row in rows:
                ids.append(row[0])

        except Exception as e:
            error_str = str(e)
            print ("Error: unable to insert data, " + error_str)

        circuits = []
        for id in ids:
            circuits.append(self._get_points_for_circuit_id(id))

        self.close()
        return circuits

    def _get_points_for_circuit_id(self, id):
        sql = "SELECT pos_w, pos_l FROM points WHERE circuits_id = %s"
        data = [id]
        points = []
        try:
            # Execute the SQL command
            self.cursor.execute(sql, data)
            # Fetch all the rows in a list of lists.
            rows = self.cursor.fetchall()
            for row in rows:
                points.append(Point(row[0], row[1]))

        except Exception as e:
            error_str = str(e)
            print ("Error: unable to insert data, " + error_str)
        return points
