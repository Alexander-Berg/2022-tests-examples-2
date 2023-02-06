#!/usr/bin/env python

import re
import time
import glob
import socket
import logging
import optparse
import datetime
import subprocess

config = {'package_name': 'yandex-web4-www-static',
          'package_path': '/usr/local/www/static.yandex.net/web4/',
          'dpkg_log_path': '/var/log/dpkg.log',
          'execute_hosts': ['pstatic-rc.yandex.net', 'pstatic-rc-s1.yandex.net']}

def remove_old_web4_packages():
    all_packages = [x.split('/')[-1] for x in glob.glob('/usr/local/www/static.yandex.net/web4/*')]
    last_days = [x[len('{}-'.format(config['package_name'])):] for x in get_packages_from_apt() if x.find(config['package_name']) >= 0]
    result = set(all_packages) - set(last_days) - set(['_'])
    for pkg in result:
        cmd = 'rm -rf {}{}'.format(config['package_path'], pkg)
        subprocess.check_output(cmd, shell=True, stderr=None)
    if result:
        print_formated('ok', 'old {} packages was removed'.format(config['package_name']))
    else:
        print_formated('ok', 'not founded old {} packages'.format(config['package_name']))

def get_packages_from_apt():
    packages = []
    cmd = "zfgrep --no-filename 'status installed' {}*".format(config['dpkg_log_path'])
    tmp = subprocess.check_output(cmd, shell=True, stderr=None)
    tmp = re.split("\n", tmp)
    for item in tmp:
        item = re.split("\s+", item)
        if len(item) == 1:
           continue
        else:
           date_time = item[0] + ' ' + item[1]
           pattern = '%Y-%m-%d %H:%M:%S'
           epochFrom = int(time.mktime(time.strptime(date_time, pattern)))
           startEpoch   = int(datetime.datetime.now().strftime("%s")) - 30 * (24 * 60 * 60)
           if epochFrom > startEpoch:
               item[4] = re.split(":", item[4])[0]
               packages.append(item[4])
    return packages

def print_formated(status, text):
    if status == 'ok':
        print('0;{}'.format(text))
    elif status == 'warn':
        print('1;{}'.format(text))
    else:
        print('2;{}'.format(text))

def main():
    try:
        host_is = socket.getfqdn()
        if host_is in config['execute_hosts']:
            remove_old_web4_packages()
        else:
            print_formated('ok', 'check was skipped')
    except Exception as e:
        print_formated('crit', 'cannot check remove {} packages in testing'.format(config['package_name']))
        
if __name__ == '__main__':
    p = optparse.OptionParser(usage='%prog [options]',
                              version='1.0')
    p.add_option('-v', '--verbose', action='store_true', help='enable output to console')
    (options, args) = p.parse_args()

    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s] [%(process)d] [%(threadName)s] %(message)s',
                        level=logging.INFO)

    if not options.verbose:
        logging.getLogger(__name__).disabled = True

    logger = logging.getLogger(__name__)
    main()
