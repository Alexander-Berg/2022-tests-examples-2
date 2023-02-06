import importlib
import os


class Plotter:
    def __init__(self):
        self.pl = importlib.import_module('matplotlib.pyplot')

    def PlotMetadata(self, metadata_file):
        plots_text = open(metadata_file).read().split('---newplot---')
        plots_ls = [p.strip().split('\n') for p in plots_text if len(p.strip())]
        plots = []
        for p in plots_ls:
            plots.append({})
            for line in p:
                if ' ' not in line:
                    continue
                key, val = line.strip().split(' ', 1)
                if key == 'name':
                    plots[-1]['name'] = '.' + val
                elif key.isdigit():
                    plots[-1]['cols'] = plots[-1].get('cols', {})
                    plots[-1]['cols'][int(key)] = val
        return plots

    def DoPlot(self, data_file, plot_file):
        data = [l.strip().split() for l in open(data_file, 'r').readlines() if len(l.strip())]
        if len(data) == 0:
            return
        metadata_file = data_file.replace('.txt', '.meta.txt')
        numlines = len(data[0]) - 1
        x = [float(l[0]) for l in data]

        default_cols = dict([
            (i+1, str(i+1))
            for i in range(numlines)
        ])

        plots_list = []
        if os.path.exists(metadata_file):
            plots_list = self.PlotMetadata(metadata_file)
        if not plots_list:
            plots_list.append({'cols': default_cols})

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

        for plot in plots_list:
            labels = []
            cols = plot.get('cols', default_cols)
            fig = self.pl.figure()
            size_in = fig.get_size_inches()
            fig.set_size_inches(2*size_in[0], 2*size_in[1])
            wasLabel = False
            for c, lb in cols.items():
                labels.append(lb)
                if wasLabel:
                    npl = self.pl.twinx()
                else:
                    wasLabel = True
                    npl = self.pl.subplot(111)
                npl.set_ylabel(lb)
                p, = npl.plot(x, [float(line[c]) for line in data], label=lb, color=colors[len(labels) - 1])
                npl.yaxis.get_label().set_color(p.get_color())

            self.pl.savefig(plot_file.replace('.png', plot.get('name', '') + '.png'))
            self.pl.close()
