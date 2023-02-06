import importlib
import sys


def inject_fixtures(target_modname, modnames, package=None):
    target_mod = sys.modules[target_modname]
    names = set(getattr(target_mod, '__all__', ()))
    for key, value in _collect_fixtures(modnames, package):
        setattr(target_mod, key, value)
        names.add(key)
    target_mod.__all__ = sorted(names)


def _collect_fixtures(modnames, package):
    for modname in modnames:
        mod = importlib.import_module(modname, package)
        for key, value in mod.__dict__.items():
            if key.startswith('pytest_'):
                raise RuntimeError(
                    f'Failed to inject {modname}.{key} symbol. '
                    'inject_fixtures() does not support full-featured pytest '
                    'plugins. Only pytest fixtures can be injected.',
                )
            if _is_fixture(value):
                yield key, value


def _is_fixture(obj):
    return hasattr(obj, '_pytestfixturefunction')
