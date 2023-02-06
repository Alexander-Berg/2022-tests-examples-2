import collections
import dataclasses
import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
import warnings

_ANY_STRING_PATTERN = r'([a-zA-Z\-\_0-9]+)'
_ANY_DIGITS_PATTERN = '([0-9]+)'


class BaseError(Exception):
    pass


class UncoveredEndpointsError(BaseError):
    pass


class UnsupportedPathParamType(BaseError):
    pass


@dataclasses.dataclass(repr=False, frozen=True)
class PathParam:
    name: str
    type_param: str
    value_enum: Optional[List[str]] = None


class Endpoint:
    def __init__(
            self,
            http_path: str,
            http_method: str,
            status_code: Optional[int] = None,
            content_type: Optional[str] = None,
    ) -> None:
        self.http_path = self._normalize(http_path)
        self.http_method = http_method
        self.status_code = status_code
        self.content_type = content_type

    def __hash__(self) -> int:
        return hash(
            (
                self.http_path,
                self.http_method,
                self.status_code,
                self.content_type,
            ),
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Endpoint):
            return False

        if self.http_path != other.http_path:
            return False

        if self.http_method != other.http_method:
            return False

        if self.status_code != other.status_code:
            return False

        if self.content_type != other.content_type:
            return False

        return True

    def __str__(self) -> str:
        str_repr = f'{self.http_method} {self.http_path}'
        if self.status_code:
            str_repr += f' response={self.status_code}'
        if self.content_type:
            str_repr += f' content-type={self.content_type}'
        return str_repr

    @staticmethod
    def _ensure_leading_separator(url: str) -> str:
        if url.startswith('/'):
            return url
        return '/' + url

    @staticmethod
    def _ensure_no_trailing_separator(url: str) -> str:
        if url.endswith('/'):
            return url[:-1]
        return url

    @staticmethod
    def _drop_query_params(url: str) -> str:
        return url.split('?', 1)[0]

    @classmethod
    def _normalize(cls, url: str) -> str:
        url = cls._drop_query_params(url)
        url = cls._ensure_leading_separator(url)
        url = cls._ensure_no_trailing_separator(url)
        return url


class SchemaEndpoint(Endpoint):
    def __init__(
            self,
            http_path: str,
            http_method: str,
            path_params: List[PathParam],
            status_code: Optional[int] = None,
            content_type: Optional[str] = None,
    ) -> None:
        super().__init__(
            http_path=http_path,
            http_method=http_method,
            status_code=status_code,
            content_type=content_type,
        )
        self._pattern: re.Pattern = self._create_pattern(
            path=self.http_path, path_params=path_params,
        )

    @classmethod
    def _create_pattern(
            cls, path: str, path_params: List[PathParam],
    ) -> re.Pattern:
        pattern = path.replace('/', r'\/')

        # substitute every path-parameter
        for param in path_params:
            if param.type_param == 'string':
                if param.value_enum:
                    pattern = pattern.replace(
                        f'{{{param.name}}}',
                        '(' + '|'.join(param.value_enum) + ')',
                    )
                else:
                    pattern = pattern.replace(
                        f'{{{param.name}}}', _ANY_STRING_PATTERN,
                    )
            elif param.type_param == 'integer':
                pattern = pattern.replace(
                    f'{{{param.name}}}', _ANY_DIGITS_PATTERN,
                )
            else:
                raise UnsupportedPathParamType(
                    f'For endpoint \'{path}\' there is'
                    ' unsupported path-param type: '
                    f' name={param.name}, type={param.type_param}',
                )

        return re.compile(pattern)

    def matches(self, url: Endpoint) -> bool:
        if self.http_method != url.http_method:
            return False

        if self.status_code != url.status_code:
            return False

        if self.content_type and self.content_type != url.content_type:
            return False

        if not self._pattern.fullmatch(url.http_path):
            return False

        return True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Endpoint):
            return False

        if not self.matches(other):
            return False

        return True

    def __hash__(self) -> int:
        # pylint: disable=useless-super-delegation
        return super().__hash__()


@dataclasses.dataclass
class CoverageStatReport:
    covered_endpoints: List[SchemaEndpoint]
    uncovered_endpoints: List[SchemaEndpoint]
    covered_endpoints_not_in_schemas: List[Endpoint]
    coverage_ratio: float
    endpoints_usage_stat: Dict[Endpoint, int]
    total_endpoints_in_schema: int

    def to_json(self) -> Dict:
        json_repr = {
            'covered_endpoints': self._group_collection(
                self.covered_endpoints,
            ),
            'uncovered_endpoints': self._group_collection(
                self.uncovered_endpoints,
            ),
            'covered_endpoints_not_in_list': self._group_collection(
                self.covered_endpoints_not_in_schemas,
            ),
            'coverage_ratio': self.coverage_ratio,
            'endpoints_usage_stat': {
                'squashed_stat': {
                    str(item): count
                    for item, count in self.endpoints_usage_stat.items()
                },
                'length': len(self.endpoints_usage_stat),
            },
        }
        return json_repr

    @staticmethod
    def _group_collection(
            endpoints_list: Union[List[Endpoint], List[SchemaEndpoint]],
    ) -> Dict[str, List[str]]:
        pretty: Dict = collections.defaultdict(list)
        for endpoint in endpoints_list:
            base_endpoint = f'{endpoint.http_method} {endpoint.http_path}'
            response = f'code={endpoint.status_code}'
            if endpoint.content_type:
                response += f' content-type=\'{endpoint.content_type}\''
            pretty[base_endpoint].append(response)
        return {
            endpoint: responses
            for endpoint, responses in sorted(
                pretty.items(), key=lambda item: (item[0], len(item[0])),
            )
        }

    def save_to_file(self, path: str) -> None:
        with open(path, 'w') as report_file:
            json.dump(self.to_json(), report_file, indent=4)

    def coverage_validate(self, strict=True) -> None:
        if self.total_endpoints_in_schema != len(self.covered_endpoints):
            group_endpoints = self._group_collection(self.uncovered_endpoints)
            repr_ = ''
            for endpoint, responses in group_endpoints.items():
                repr_ += (
                    '  - {0}\n'
                    '    Uncovered responses:\n'
                    '{1}\n'.format(
                        endpoint, '\n'.join(f'      - {x}' for x in responses),
                    )
                )

            message = (
                'API coverage check failed! Please write tests '
                'for the following endpoints: \n{0}'.format(repr_)
            )
            if strict:
                raise UncoveredEndpointsError(message)
            warnings.warn(message)


class CoverageReport:
    def __init__(self) -> None:
        self._endpoints_usage_stat: List[Endpoint] = []

    def update_usage_stat(
            self,
            http_path: str,
            http_method: str,
            response_code: Optional[int] = None,
            content_type: Optional[str] = None,
    ) -> None:
        self._endpoints_usage_stat.append(
            Endpoint(
                http_path=http_path,
                http_method=http_method,
                status_code=response_code,
                content_type=content_type,
            ),
        )

    def _squash_usage_stat(self) -> Dict[Endpoint, int]:
        squashed_stat: Dict[Endpoint, int] = {}
        for stat_endpoint in self._endpoints_usage_stat:
            if stat_endpoint in squashed_stat:
                squashed_stat[stat_endpoint] += 1
            else:
                squashed_stat[stat_endpoint] = 1
        return squashed_stat

    @staticmethod
    def _get_covered(
            squashed_stat: Dict[Endpoint, int],
            service_endpoints: List[SchemaEndpoint],
    ) -> List[SchemaEndpoint]:
        covered: List[SchemaEndpoint] = []

        for stat_endpoint in squashed_stat.keys():
            for endpoint in service_endpoints:
                if endpoint.matches(stat_endpoint) and endpoint not in covered:
                    covered.append(endpoint)
        return covered

    @staticmethod
    def _get_covered_not_in_schema(
            squashed_stat: Dict[Endpoint, int], covered: List[SchemaEndpoint],
    ) -> List[Endpoint]:
        return [
            endpoint
            for endpoint in squashed_stat.keys()
            if endpoint not in covered
        ]

    def generate_report(
            self, service_endpoints: List[SchemaEndpoint],
    ) -> CoverageStatReport:
        squashed_stat = self._squash_usage_stat()

        covered_endpoints: List[SchemaEndpoint] = self._get_covered(
            squashed_stat, service_endpoints,
        )

        # pylint: disable=invalid-name
        covered_endpoints_not_in_schemas = self._get_covered_not_in_schema(
            squashed_stat, covered_endpoints,
        )

        uncovered_endpoints: List[SchemaEndpoint] = list(
            set(service_endpoints) - set(covered_endpoints),
        )

        coverage_ratio = 1.0
        if service_endpoints:
            coverage_ratio = len(covered_endpoints) / len(service_endpoints)

        return CoverageStatReport(
            covered_endpoints=covered_endpoints,
            uncovered_endpoints=uncovered_endpoints,
            covered_endpoints_not_in_schemas=covered_endpoints_not_in_schemas,
            coverage_ratio=coverage_ratio,
            endpoints_usage_stat=squashed_stat,
            total_endpoints_in_schema=len(service_endpoints),
        )
