class BooleanFlagCases:
    def __init__(self, cases):
        self.cases = [
            [case == own_case for own_case in cases] for case in cases
        ]
        self.ids = cases

    def get_names(self):
        return ','.join(self.ids)

    def get_ids(self):
        return self.ids

    def get_args(self):
        return self.cases
