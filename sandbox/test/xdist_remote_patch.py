import sys

import py  # noqa

# There's no need to include this module into any Arcadia binary/library/test,
# but I'll left this protection code here anyway.
if not getattr(sys, "is_standalone_binary", False):  # Just to suppress import test errors, cannot import `system` here
    exec_dict = dict(globals())
    import xdist.remote

    prev_name, exec_dict['__name__'] = __name__, ''
    path = xdist.remote.__file__.split('.')
    path[-1] = 'py'
    co = compile(open('.'.join(path)).read(), '<remote exec>', 'exec')
    exec(co, exec_dict)
    exec_dict['__name__'] = prev_name

    class SlaveInteractor(exec_dict['SlaveInteractor']):
        def run_tests(self, torun):
            items = self.session.items
            if torun:
                self.item_index = torun.pop(0)
                nextitem = items[torun[0]] if torun else items[self.item_index]
            else:
                nextitem = None
            self.config.hook.pytest_runtest_protocol(
                item=items[self.item_index],
                nextitem=nextitem)

    exec_dict['SlaveInteractor'] = SlaveInteractor

    class HackedDict(dict):
        def __setitem__(self, name, value):
            if name != 'SlaveInteractor':
                dict.__setitem__(self, name, value)

    exec(co, HackedDict(exec_dict))
