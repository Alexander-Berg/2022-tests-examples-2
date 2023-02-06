import re
import pandas as pd
from dmp_suite.yt.meta import YTMeta
from dmp_suite.yql.operation import YqlSelect


class YqlQueryTest:
    def __init__(self, query):
        sources = re.findall(r'\{.*?\}', query)
        if '{target_path}' not in sources:
            raise Exception('Invalid query, target_path is missing!')
        query = query.replace('{target_path}', '@result')
        for source in sources:
            query = query.replace(source, '$'+source[1:-1])
        self.query = query

        self.sources = list(map(lambda src:src[1:-1], sources))
        self.sources.append('target')
        self.sources.remove('target_path')
        self.rules = {}

    def add_source(self, source, table, fields=None):
        if source in ('result', 'target', 'target_name'):
            raise Exception('To specify target use add_target method')
        elif source not in self.sources:
           raise Exception('Unknow source table')
        else:
            fields_from_meta = list(map(lambda field:field['name'], YTMeta(table).yt_schema()))
            fields_from_meta.remove('etl_updated')
            if fields:
                if set(fields).issubset(set(fields_from_meta)):
                    self.current_fields = fields
                else:
                    raise Exception('Table lacks specified attributes')
            else:
                self.current_fields = fields_from_meta
            self.current_source = source
            return self

    def add_target(self, table, fields=None):
        fields_from_meta = list(map(lambda field:field['name'], YTMeta(table).yt_schema()))
        fields_from_meta.remove('etl_updated')
        if fields:
            if set(fields).issubset(set(fields_from_meta)):
                self.current_fields = fields
            else:
                raise Exception('Table lacks specified attributes')
        else:
            self.current_fields = fields_from_meta
        self.target_fields = self.current_fields
        self.current_source = 'target'
        return self

    def from_path(self, path):
        if self.current_source:
            self.rules[self.current_source] = '${source} = ( select {fields} from `{path}`);'.format(
                source=self.current_source,
                fields=','.join(self.current_fields),
                path=path
            )
            self.current_source = None
            return self
        else:
            raise Exception('Use either add_source or add_target before using from method')

    def from_data(self, data):
        if self.current_source:
            self.rules[self.current_source] = '${source} = ('.format(source=self.current_source)
            lines = []
            for row in data:
                current_line = 'select '
                for value, field in zip(row, self.current_fields):
                    current_line += str(value)+' as '+field+','
                lines.append(current_line[:-1])
            self.rules[self.current_source] += '\nunion all\n'.join(lines) + ');'
            self.current_source = None
            return self
        else:
            raise Exception('Use either add_source or add_target before using from method')

    def isprepared(self):
        return sorted(self.sources)==sorted(self.rules.keys())

    def get_result(self):
        if not self.isprepared():
            raise Exception('Not all sources and/or target specified!')
        else:
            query = '\n'.join([self.rules[key] for key in self.rules.keys() if key!='target']) + \
                '\ncommit;\n' + self.query + '\ncommit;\n' + 'select * from @result'
            yql_select = YqlSelect(query)
            self.result = yql_select.get_data()
            return self.result

    def get_target(self):
        yql_select = YqlSelect(self.rules['target']+'\nselect * from $target')
        self.target = yql_select.get_data()
        return self.target

    def check(self):
        result = self.get_result()
        target = self.get_target()
        merged = result.merge(target, indicator=True, how='outer')
        return(merged['_merge'].eq('both').all())

    
