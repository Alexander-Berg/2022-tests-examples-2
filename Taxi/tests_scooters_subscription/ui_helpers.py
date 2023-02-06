import typing


def section(items: typing.List, title=None, **kwargs):
    return {'title': title or atext([]), 'items': items, **kwargs}


def group(items: typing.List, title=None, meta_style: str = None):
    return {
        'type': 'group',
        **({'title': title} if title else {}),
        'items': items,
        **({'meta_style': meta_style} if meta_style else {}),
    }


def grid(rows: typing.List[typing.List]):
    return {'type': 'grid', 'rows': [{'cells': row} for row in rows]}


def cell(title: typing.List, **kwargs):
    return {'title': title, **kwargs}


def atext(items: typing.List, **kwargs):
    return {'items': items, **kwargs}


def text(txt: str, **kwargs):
    return {'type': 'text', 'text': txt, **kwargs}


def badge(title, **kwargs):
    return {'title': title, **kwargs}
