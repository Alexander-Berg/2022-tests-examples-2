import pandas as pd

from .draw import Draw


class Tests:
    report = '<h1>Percentage of selected documents<br>' \
             '&mdash; from test datasets</h1>\n'
    counts = pd.DataFrame()

    tests = []
    datasets = {}

    def __init__(self, args):
        self.load(args)
        self.calc()
        self.draw(args)

    def load(self, args):
        table = args.client.read_table(args.work_dir + '/tests')
        self.counts = pd.DataFrame().from_dict(list(table))

        self.tests = self.counts['Test'].unique()

        for test, counts in self.counts.groupby('Test'):
            self.datasets[test] = counts['Dataset'].unique()

    def calc(self):
        self.counts = self.counts.pivot_table(
            index=['Formula', 'Test', 'Dataset'],
            columns='TierId',
            values='Weight'
        )
        self.counts.fillna(0, inplace=True)
        self.counts = self.counts.cumsum(axis=1)

        for tier in (0, 1):
            if tier in self.counts:
                self.counts[tier] /= self.counts[2]
        self.counts[2] /= self.counts[3]

        del self.counts[3]
        self.counts *= 100

    def draw(self, args):
        head = ['Dataset'] + args.formulas + ['In search']

        for tier in (0, 1):
            if tier not in self.counts:
                continue

            draw = Draw()

            self.report += f'<h2>Tier {tier}</h2>\n'
            table = draw.head(head)

            for test in self.tests:
                table += draw.section(test)
                datasets = self.datasets[test]

                for dataset in datasets:
                    cells = [draw.cell(dataset)]

                    key = (args.formulas[0], test, dataset)

                    draw.value = self.counts[tier][key]
                    in_search = self.counts[2][key]

                    for formula in args.formulas:
                        key = (formula, test, dataset)

                        value = self.counts[tier][key]
                        cells.append(draw.cell(draw.part(value)))

                    cells.append(draw.cell(f'{in_search:.2f}%'))

                    table += draw.row(cells)
            self.report += f'<table>{table}</table>\n'
