# pylint: disable=import-error
import argparse
import datetime
import json
import ssl
import tkinter as tk
import urllib
import urllib.parse
import urllib.request
import urllib.response

ID = ''  # paste session_id here


def parse_duration(string, now):
    splitters = [
        ('w', 'weeks'),
        ('d', 'days'),
        ('h', 'hours'),
        ('m', 'minutes'),
        ('s', 'seconds'),
    ]
    res = {}
    right = string
    for sep, key in splitters:
        try:
            left, right = right.split(sep)
            res[key] = int(left)
        except Exception:  # pylint: disable=broad-except
            continue
    return now - datetime.timedelta(**res)


def time_to_string(time):
    return time.isoformat()[:-3] + 'Z'


def do_extract():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--output',
        type=str,
        help='file to output data',
        required=True,
        dest='output_path',
    )

    args = parser.parse_args()
    output_path = args.output_path

    master = tk.Tk()
    tk.Label(master, text='Url: ').grid(row=0)
    tk.Label(master, text='Session_id: ').grid(row=1)

    entry_url = tk.Entry(master)
    entry_session_id = tk.Entry(master)

    entry_url.grid(row=0, column=1)
    entry_session_id.grid(row=1, column=1)

    def dl_data():
        base_url = entry_url.get()
        if ID:
            session_id = ID
        else:
            session_id = entry_session_id.get()

        params = urllib.parse.parse_qs(urllib.parse.urlparse(base_url).query)
        cookie = 'Session_id={id}; sessionid2={id}'.format(id=session_id)
        if 'e' not in params:
            now = datetime.datetime.utcnow()
            time_from = time_to_string(parse_duration(params['b'][0], now))
            time_to = time_to_string(now)
        else:
            time_from = params['b'][0]
            time_to = params['e'][0]
        data_value = {
            'from': time_from,
            'to': time_to,
            'program': params['expression'][0],
            'useNewFormat': False,
        }

        req = urllib.request.Request(
            'https://solomon.yandex-team.ru/api/v2/projects/taxi/sensors/data',
        )
        jsondata = json.dumps(data_value)
        jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes

        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Cookie', cookie)
        req.add_header('Content-Length', len(jsondataasbytes))

        # pylint: disable=protected-access
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(
            req, jsondataasbytes, context=context,
        )
        output_file = open(output_path, 'w')
        output_file.write(response.read().decode('utf-8'))
        output_file.close()

        master.quit()

    tk.Button(master, text='Поїхали', command=dl_data).grid(
        row=3, column=1, sticky=tk.W, pady=4,
    )
    master.mainloop()


if __name__ == '__main__':
    do_extract()
