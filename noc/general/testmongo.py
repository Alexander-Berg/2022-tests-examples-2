#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import socket
import ConfigParser
import random
import logging
from asterisk.agi import *
from common import *

def getOffice (db, callerid):
	err = False
	try:
                print("""{'From':{'$lte':int(callerid)},'$and':[{'To':{'$gte':int(callerid)}}]}""")
                document = db.getOneData({'From':{'$lte':int(callerid)},'$and':[{'To':{'$gte':int(callerid)}}]})
                print (document)
                ret = document["Office"]
	except (Exception) as e:
		err = True
		ret = str(e)
        return err, ret

def saveOverload(db, queuename, length, threshold):
        ret = False
        try:
                insertQuery = ("INSERT INTO cc_queueoverload_stat (queuename, length, threshold) VALUES (%(queuename)s), %(length)s),%(threshold)s)")
                insertData = { 'queuename': str(queuename), 'length': str(length), 'threshold': str(threshold) }
                db.execSQLInsert(insertQuery, insertData)
        except (Exception) as e:
                ret = str(e)
        return ret

def getQstate(agi, skill):
        err = False
        try:
            qstates = {}
            for region in REGIONS:
                tmpqueue = region + "_"  + skill
                numcalls = agi.get_full_variable('${QUEUE_WAITING_COUNT(' + tmpqueue +')}')
                qstates[tmpqueue] = numcalls
        except (Exception) as e:
                err = True
                qstates = str(e)
        return err, qstates

try:
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('TEST')
    callerid = sys.argv[1].strip()
    config = ConfigParser.RawConfigParser()
    config.read('/usr/local/etc/synqueue.conf')
    asteriskDB = astDB('/etc/asterisk/res_config_mysql.conf', 'asterisk_cipt_q1')
    regionURL = config.get('mongo-geophones', 'url')
    regionBase = config.get('mongo-geophones', 'db')
    regionColl = config.get('mongo-geophones', 'collection')
    regionDB = mongoDB(regionURL, regionBase, regionColl)
    stateFile = config.get('localAMI', 'state_file')
    err, office = getOffice(regionDB, callerid)
    print (office)
except (Exception) as e:
    print(e)
