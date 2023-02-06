#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import socket
import ConfigParser
from random import choice
from asterisk.agi import *
from common import *
import operator

def getOffice (db, callerid):
    err = False
    try:
        document = db.getOneData({'From':{'$lte':int(callerid)},'$and':[{'To':{'$gte':int(callerid)}}]})
        if document  == None:
            err = True
            ret = ""
        else:
            ret = document['Office']
            # Special case: if DB returns error value for undefined region/office
            # or phone is originated from Kazakhstan, behave like there was an error
            if ret == 'err' or ret == 'OrangePoint':
                err = True
                ret = ""            
    except (Exception) as e:
        err = True
        ret = str(e)
    return err, ret

def saveOverload(db, fullqueue, destqueue, length, threshold):
    ret = False
    try:
        insertQuery = ("INSERT INTO cc_queueoverload_stat (queuename, destqueue, length, threshold) VALUES ( %(fullqueue)s), %(destqueue)s), %(length)s), %(threshold)s)")
        insertData = { 'fullqueue': str(fullqueue), 'destqueue': str(destqueue), 'length': str(length), 'threshold': str(threshold) }
        db.execSQLInsert(insertQuery, insertData)
    except (Exception) as e:
        ret = str(e)
    return ret

def getQstate(agi, skill):
    err = False
    try:
        queues = {}
        for region in REGIONS:
            tmpqueue = region + "_"  + skill
            numcalls = agi.get_full_variable('${QUEUE_WAITING_COUNT(' + tmpqueue +')}')
            numops = agi.get_full_variable('${QUEUE_MEMBER_COUNT(' + tmpqueue +')}')
            queues[tmpqueue] = {"calls": numcalls, "opers": numops}
    except (Exception) as e:
        err = True
        qstates = str(e)
    return err, queues

def getBest(agi, skill, queuename):
    err, queues = getQstate(agi, skill)
    if err:
        wasError = True
        riseMsg(agi, logFile, "Cannot get state of queues. Error was: %s" % (queuesstate))
    queuelen = int(queues[queuename]['calls'])
    queueops = int(queues[queuename]['opers'])
    candidates = {}

    if queueops < 1:
        agi.verbose("no opers in %s" % queuename)
        for queue in queues:
            if queues[queue]['calls'] > 0:
                agi.verbose("add candidate %s with %s opers" % (queue, queues[queue]['opers']))
                candidates[queue] = queues[queue]['opers']
        if len(candidates) > 0:
            sorted_c = sorted(candidates.items(), key=operator.itemgetter(1))
            queuename = sorted_c[len(sorted_c)-1][0]
    else:
        if queuelen > MAXQUEUELEN:
            fullqueue = queuename
            agi.verbose("%s length %s is over threshold %s" % (queuename, queuelen, MAXQUEUELEN))
            if saveOverload(asteriskDB, fullqueue, queuename, queuelen, MAXQUEUELEN):
                riseMsg(agi, logFile, "Cannot save QueueOverload message: $s $s $s %s" % (time.localtime(), queuename, queuelen, MAXQUEUELEN))
            for queue in queues:
                if queues[queue]['calls'] < MAXQUEUELEN:
                     agi.verbose("add candidate %s with %s calls" % (queue, queues[queue]['calls']))
                     candidates[queue] = queues[queue]['calls']
            if len(candidates) > 0:
                sorted_c = sorted(candidates.items(), key=operator.itemgetter(1))
                queuename = sorted_c[0][0]
    return queuename    
   
try:
    callerid = sys.argv[1].strip()
    if len(callerid) > 10:
        callerid = callerid[-10:]
    skill = sys.argv[2].strip()
    queuename = sys.argv[3].strip()
    agi = AGI()
    config = ConfigParser.RawConfigParser()
    config.read('/usr/local/etc/synqueue.conf')
    logFile = config.get('localAMI', 'log_file')
    asteriskDB = astDB('/etc/asterisk/res_config_mysql.conf', 'asterisk_cipt_q1')
    regionURL = config.get('mongo-geophones', 'url')
    regionBase = config.get('mongo-geophones', 'db')
    regionColl = config.get('mongo-geophones', 'collection')
    regionDB = mongoDB(regionURL, regionBase, regionColl)
    
    err, office = getOffice(regionDB, callerid)
    if err:
        wasError = True
        riseMsg(agi, logFile, "Use random queue: Cannot get office for calling %s error was: %s" % (callerid, err))
        queuename = choice(REGIONS) + "_" + skill
    else:
        queuename = office + "_" + skill
    riseMsg(agi, logFile, "Proposed=%s" % queuename)
    queueto = getBest(agi, skill, queuename)
    riseMsg(agi, logFile, "QueueTo=%s" % queueto)
    queuename = queueto #"ekb_" + skill   
    agi.verbose("Queue %s is selected." % queuename)
    agi.set_variable('QUEUE_FOR_CALL', queuename)
except (Exception) as e:
    print(e)
    riseMsg(agi, logFile,"selectqueue.py: Exception " + str(e))
    agi.set_variable('QUEUE_FOR_CALL', queuename)
