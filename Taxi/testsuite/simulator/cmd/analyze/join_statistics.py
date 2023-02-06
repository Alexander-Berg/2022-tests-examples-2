import pathlib
import pickle
import pprint
from typing import Any
from typing import List
from typing import Tuple

import tabulate


class BaseError(Exception):
    pass


class NotExistError(BaseError):
    pass


class EmptyInputError(BaseError):
    pass


class StatisticsJoiner:
    """
    Load statistics of each run in specific format,
    combines it in single table.
    """

    SIMULATOR_DIR = pathlib.Path(__file__).parent.parent.parent

    TEMPLATES_DIR = SIMULATOR_DIR / 'templates'
    CASES_DIR = SIMULATOR_DIR / 'cases'

    JOINED_FILENAME = '.stats.log'

    def _validate(self, case_name: str):
        if not case_name:
            raise EmptyInputError('case-name parameter is empty')

        if not (self.CASES_DIR / case_name).exists():
            raise NotExistError(
                f'Case {case_name} folder doesnt exist in {self.CASES_DIR}',
            )

    def _search_statistic_files(
            self, case_dir: pathlib.Path,
    ) -> List[pathlib.Path]:
        paths = []
        for file in case_dir.iterdir():
            if file.is_dir():
                paths += self._search_statistic_files(file)
                continue
            if file.name == '.stats.p':
                paths.append(file)
        return paths

    def _join_files(
            self, paths: List[pathlib.Path],
    ) -> Tuple[List[str], List[Any], List[pathlib.Path]]:
        meta_headers: List[str] = []
        rows: List[Any] = []
        result_paths: List[pathlib.Path] = []
        for path in paths:
            with open(path, 'rb') as file:
                try:
                    headers, row = pickle.load(file=file)
                except EOFError:
                    print(f'Empty file at path "{path}", skipped')
                    continue

                if not meta_headers:
                    meta_headers = [str(h) for h in headers]
                else:
                    file_headers = [str(h) for h in headers]
                    for file_header, meta_header in zip(
                            file_headers, meta_headers,
                    ):
                        assert (
                            file_header == meta_header
                        ), f'{path.parts[-2]}: {file_header} vs {meta_header}'
                    assert len(file_headers) == len(meta_headers)
                rows.append(row)
                result_paths.append(path)
        return meta_headers, rows, result_paths

    def join(
            self,
            case_name: str,
            headers_projection: List[str],
            transpose: bool = False,
    ):
        print(f'Combining statistics for CASE="{case_name}"\n')

        # validate input
        self._validate(case_name=case_name)

        case_dir = self.CASES_DIR / case_name

        # search for .stats.p
        paths = self._search_statistic_files(case_dir=case_dir)
        if not paths:
            print('No paths provided, do nothing')
            return

        headers, rows, non_empty_paths = self._join_files(paths)
        print('All headers: ')
        pprint.pprint(headers)
        print()

        if headers_projection:
            for header in headers_projection:
                assert (
                    headers.count(header) <= 1
                ), 'Only unique headers projection allowed'
            # deletes non selected headers
            for i, header in reversed(list(enumerate(headers[:]))):
                if header not in headers_projection:
                    del headers[i]
                    for row in rows:
                        del row[i]
            # rearrange headers
            indexes = [
                headers.index(h) for h in headers_projection if h in headers
            ]
            headers = [headers[i] for i in indexes]
            for i, row in enumerate(rows):
                rows[i] = [row[j] for j in indexes]

            if set(headers) != set(headers_projection):
                print(
                    'WARNING: Requested headers projection differ from result',
                )
            print('Use headers projection: ')
            pprint.pprint(headers)
            print()

            assert headers, 'Empty result headers'

        headers.insert(0, 'parameters')
        for row, path in zip(rows, non_empty_paths):
            row.insert(0, path.parts[-2])

        rows.insert(0, headers)
        if transpose:
            rows = list(map(list, zip(*rows)))

        joined = tabulate.tabulate(rows, headers='firstrow')
        with open(case_dir / self.JOINED_FILENAME, 'w') as file:
            file.write(joined)
            file.write('\n')
