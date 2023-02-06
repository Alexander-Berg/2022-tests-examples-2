import json
import sys


def running_operation():
    json.dump({'status': 'running', 'result': 'undefined'}, sys.stdout)


def failed_operation():
    json.dump({'status': 'completed', 'result': 'failure'}, sys.stdout)


def successed_operation():
    json.dump({'status': 'completed', 'result': 'success'}, sys.stdout)


def status():
    if 'failed' in sys.argv[-1]:
        json.dump({'status': 'completed', 'result': 'failure'}, sys.stdout)
    elif 'successed' in sys.argv[-1]:
        json.dump({'status': 'completed', 'result': 'success'}, sys.stdout)
    elif 'running' in sys.argv[-1]:
        json.dump({'status': 'running', 'result': 'undefined'}, sys.stdout)
