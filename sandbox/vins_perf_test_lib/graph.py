import argparse
from functools import partial


def plot_sensors(sensors_data, graph_path):
    import plotly.graph_objs as go
    import plotly.offline as py
    data = []
    for k, v in sensors_data.iteritems():
        v['time'], v['value'] = zip(*sorted(zip(v['time'], v['value'])))
        data.append(
            go.Scatter(
                x=v['time'],
                y=v['value'],
                name=k
            )
        )
    fig = go.Figure(data)
    py.plot(fig, filename=graph_path)


def plot_quantiles(old, new, old_name, new_name, graph_path):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from sensors_loader import unite_sensors_keys

    unite_sensors_keys(old, new)
    _, ax = plt.subplots(nrows=len(old.keys()), figsize=(16, 9 * len(old.keys())), tight_layout=True)
    for i, k in enumerate(old.keys()):
        ax[i].title.set_text(k)
        ax[i].plot(sorted(old[k]['value']), np.linspace(0, 100, len(old[k]['value'])), label=old_name)
        ax[i].plot(sorted(new[k]['value']), np.linspace(0, 100, len(new[k]['value'])), label=new_name)
        ax[i].legend()
        ax[i].set_ylabel('percentile')
        ax[i].set_xlabel('time (ms)')
        ax[i].grid(axis='both')
    plt.savefig(graph_path, format='svg')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', choices=['vins', 'megamind'])
    parser.add_argument('--stable-sensors-path', default=None)
    parser.add_argument('--test-sensors-path')
    parser.add_argument('--stable-package-name', default=None)
    parser.add_argument('--test-package-name')
    parser.add_argument('--all-sensors-stable-graph-path', default=None)
    parser.add_argument('--all-sensors-test-graph-path')
    parser.add_argument('--quantiles-graph-path', default=None)
    args = parser.parse_args()

    import sensors_loader

    if args.service == 'vins':
        loader = partial(sensors_loader.load_data, date_parser=sensors_loader.parse_date_vins,
                         sensor_filter=sensors_loader.sensor_filter_vins,
                         name_extractor=sensors_loader.extract_name_vins)
    elif args.service == 'megamind':
        loader = partial(sensors_loader.load_data, date_parser=sensors_loader.parse_date_mm,
                         sensor_filter=sensors_loader.sensor_filter_mm, name_extractor=sensors_loader.extract_name_mm)

    plot_sensors(loader(args.test_sensors_path), args.all_sensors_test_graph_path)
    if args.stable_package_name:
        plot_sensors(loader(args.stable_sensors_path), args.all_sensors_stable_graph_path)
        plot_quantiles(loader(args.stable_sensors_path, filter_warm_up=True),
                       loader(args.test_sensors_path, filter_warm_up=True), args.stable_package_name,
                       args.test_package_name, args.quantiles_graph_path)
