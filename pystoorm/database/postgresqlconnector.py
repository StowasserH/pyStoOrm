#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"
import logging
from .connector import Connector
import mysql.connector
from .table import Table
from .column import Column
from .schema import Schema
from .reference import Reference

logger = logging.getLogger(__name__)


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class PostgresqlConnector(Connector):
    con = None
    args = None
    modded_attr = {"user": "username", "passwd": "password", "db": "database", "connect_timeout": "connection_timeout"}

    allowed_attributes = ("username", "password", "database", "host", "port", "unix_socket"
                          , "auth_plugin", "use_unicode", "charset", "collation", "autocommit", "time_zone"
                          , "sql_mod", "get_warnings", "raise_on_warnings", "connection_timeout"
                          , "client_flags", "buffered", "raw", "consume_results", "ssl_ca", "ssl_cert", "ssl_disabled"
                          , "ssl_key", "ssl_verify_cert", "ssl_verify_identity", "force_ipv6", "dsn", "pool_name"
                          , "pool_size", "pool_reset_session", "compress", "converter_class", "failover"
                          , "option_files", "option_groups", "allow_local_infile", "use_pure")

    def get_cursor(self):
        if self.con is None:
            self.connect()
        return self.con.cursor()

    def populate_args(self, config):
        for attr in self.allowed_attributes:
            if attr in config:
                self.args[attr] = config[attr]
        for attr in self.modded_attr:
            if attr in config:
                self.args[self.modded_attr[attr]] = config[attr]
                # normalize also the data in the configuration:
                self.config[self.modded_attr[attr]] = config[attr]

    def connect(self):
        self.args = {}

        self.populate_args(self.config)

        if "passfile" in self.config:
            passfile = self.config["passfile"]
            logger.info(f'Parsing MySQL passfile: {passfile}')
            import configparser
            config = configparser.ConfigParser()
            config.read(passfile)
            if "client" in config:
                client = config["client"]
                self.populate_args(client)

        logger.debug(f'Connecting to MySQL {self.args.get("username", "unknown")}@{self.args.get("host", "unknown")}')
        logger.debug(f'Used params: {", ".join(self.args.keys())}')
        try:
            self.con = mysql.connector.connect(**self.args)
            logger.info("Successfully connected to MySQL")
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise

    def get_schema(self):
        cur = self.get_cursor()
        anz = cur.execute("SHOW TABLES")
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
        tupple = "DATA_TYPE, IS_NULLABLE, COLUMN_KEY,COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION"
        querry = "SELECT " + tupple + " FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = %s AND table_schema = %s AND column_name = %s;"
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

        cur = self.get_cursor()
        tupple = "REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME"
        where = "TABLE_NAME = %s AND TABLE_SCHEMA = %s AND COLUMN_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL"
        querry = "SELECT " + tupple + " FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE " + where + ";"
        cur.execute(querry, (table, self.config['database'], column))
        result = cur.fetchall()
        for ref in result:
            ret.add_ref_to(Reference(ref[0], ref[1], ref[2]))
        cur.close()

        cur = self.get_cursor()
        tupple = "TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME"
        where = "REFERENCED_TABLE_NAME = %s AND REFERENCED_TABLE_SCHEMA = %s AND REFERENCED_COLUMN_NAME = %s"
        querry = "SELECT " + tupple + " FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE " + where + ";"
        cur.execute(querry, (table, self.config['database'], column))
        result = cur.fetchall()
        for ref in result:
            ret.add_ref_from(Reference(ref[0], ref[1], ref[2]))
        cur.close()

        return ret
