import contextlib
import typing

from . import matching


class _DroppedItem:
    pass


_dropped = _DroppedItem()  # pylint: disable=invalid-name


class BaseContext:
    allow_matching: bool = False
    params: typing.Dict[str, typing.Any]

    @contextlib.contextmanager
    def with_matching(self, allow_matching=False):
        saved = self.allow_matching
        self.allow_matching = allow_matching
        try:
            yield
        finally:
            self.allow_matching = saved


class Context(BaseContext):
    def __init__(self, params: typing.Optional[dict] = None):
        self.params = params or {}


class StackedContext(BaseContext):
    def __init__(self, params: typing.Optional[dict] = None):
        self._path = [Context(params=params)]

    @property
    def params(self):
        return self._path[-1].params

    @contextlib.contextmanager
    def context(self, params=None):
        new_params = self.params.copy()
        if params:
            new_params.update(params)
        context = Context(new_params)
        self._path.append(context)
        try:
            yield context
        finally:
            assert self._path[-1] is context
            self._path.pop(-1)


def render(value, context: BaseContext, *, allow_matching: bool = False):
    with context.with_matching(allow_matching):
        return _render_item(value, context)


def _render_dict(doc: dict, context):
    if len(doc) == 1:
        for key, value in doc.items():
            if key in _OPERATORS:
                return _OPERATORS[key](value, context)
    result = {}
    for key, value in doc.items():
        value = _render_item(value, context)
        if value is not _dropped:
            result[key] = value
    return result


def _render_list(value: list, context):
    result = []
    for item in value:
        item = _render_item(item, context)
        if item is not _dropped:
            result.append(item)
    return result


def _render_item(item, context):
    if isinstance(item, dict):
        return _render_dict(item, context)
    if isinstance(item, list):
        return _render_list(item, context)
    return item


def _operator_param(item, context):
    assert isinstance(item, dict)
    assert 'name' in item
    name = item['name']
    if 'default' in item:
        return context.params.get(name, item['default'])
    if item.get('ifExists'):
        return context.params.get(name, _dropped)
    if item.get('nullable'):
        return context.params.get(name, None)
    value = _resolve(context, name, _dropped)
    if value is _dropped:
        raise KeyError(f'Cannot resolve parameter {name}')
    return value


def _resolve(context, name, default):
    if name[:1] == '/':
        return _resolve_pointer(context.params, name[1:], default)
    return context.params.get(name, default)


def _resolve_pointer(root, path, default):
    parts = path.split('/')
    for part in parts:
        if isinstance(root, (list, tuple)):
            part = int(part)
            try:
                root = root[part]
            except IndexError:
                return default
        elif isinstance(root, dict) or hasattr(root, '__getitem__'):
            try:
                root = root[part]
            except KeyError:
                return default
        else:
            try:
                root = getattr(root, part)
            except AttributeError:
                return default
    return root


_OPERATORS = {'$param': _operator_param, '$match': matching.operator_match}
