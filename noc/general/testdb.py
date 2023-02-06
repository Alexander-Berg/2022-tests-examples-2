#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import socket
import ConfigParser
from common import *

config = ConfigParser.RawConfigParser()
config.read('/usr/local/etc/synqueue.conf')
qmDB = astDB('/etc/asterisk/res_config_mysql.conf', 'qm_cipt_q1')
agentQueues = getAgentQueues(qmDB, '7264')
print(agentQueues)
