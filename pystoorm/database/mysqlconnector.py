#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"
import logging
from .connector import Connector
import mysql.connector
from .table import Table
from .column import Column
from .schema import Schema

logger = logging.getLogger(__name__)


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class MysqlConnector(Connector):
    con = None

    def get_cursor(self):
        if self.con is None:
            self.connect()
        return self.con.cursor()

    def connect(self):
        logger.info(f"Connecting to MySQL at {self.config['host']}")
        try:
            self.con = mysql.connector.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['username'],
                passwd=self.config['password']
            )
            logger.info("Successfully connected to MySQL")
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise

    def get_schema(self):
        cur = self.get_cursor()
        cur.execute("SHOW TABLES")
        tab_namen = [item[0] for item in cur.fetchall()]
        cur.close()
        return Schema(self.config['database'], tab_namen)

    def get_table(self, table):
        cur = self.get_cursor()
        cur.execute("SHOW COLUMNS FROM `%s`" % table)
        feldnamen = [item[0] for item in cur.fetchall()]
        cur.close()
        return Table(table, "flat", feldnamen)

    def get_column(self, table, column):
        cur = self.get_cursor()
        tupple = ("DATA_TYPE, IS_NULLABLE, COLUMN_KEY,COLUMN_DEFAULT, "
                  "CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION")
        querry = ("SELECT " + tupple + " FROM INFORMATION_SCHEMA.COLUMNS "
                  "WHERE table_name = %s AND table_schema = %s AND column_name = %s;")
        cur.execute(querry, (table, self.config['database'], column))
        result = cur.fetchall()
        if not result:
            raise ValueError(f"Column {column} not found in table {table}")
        result = result[0]
        length = 0
        if result[4]:
            length = int(result[4])
        elif result[5]:
            length = int(result[5])
        ret = Column(column, result[0], result[1] == "YES", result[2], result[3], length)
        cur.close()
        return ret
