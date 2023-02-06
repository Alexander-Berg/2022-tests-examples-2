# pylint: disable=import-error
# brew install libpng freetype pkg-config
# pip3 install -U matplotlib argparse
import argparse
import datetime
import json

from matplotlib import dates
import matplotlib.pyplot as plt


def plot_timeseries(data, fig):
    timeseries = data['timeseries']
    alias = timeseries['alias']
    timestamps = [
        datetime.datetime.fromtimestamp(x / 1000)
        for x in timeseries['timestamps']
    ]
    values = timeseries['values']

    axis = fig.add_subplot()
    axis.set_facecolor((0.16, 0.16, 0.16))
    axis.xaxis.set_major_formatter(dates.DateFormatter('%m/%d %H:%M'))
    axis.plot(timestamps, values, label=alias)


def do_plot():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--file',
        '-f',
        action='append',
        type=str,
        help='list of files with data',
        required=True,
        dest='files',
    )

    args = parser.parse_args()
    files = args.files

    plt.style.use('dark_background')

    fig = plt.figure()
    fig.patch.set_facecolor((0.12, 0.12, 0.12))

    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            if 'vector' in data:
                for timeseries in data['vector']:
                    plot_timeseries(timeseries, fig)
            else:
                plot_timeseries(data, fig)

    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.3)

    plt.legend()
    plt.show()


if __name__ == '__main__':
    do_plot()
