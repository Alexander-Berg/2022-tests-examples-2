import attr
from easytap import Tap

from pahtest import config, typing as t
from pahtest.file import YmlFile
from pahtest.folder import Folder
from pahtest.results import ActionResult, Note, Results, TapResult


@attr.s(auto_attribs=True)
class Elapsed:
    min: float = 0.0
    max: float = 0.0


@attr.s(auto_attribs=True)
class Check:
    success: bool = True
    description: str = ''
    message: str = ''
    tap_description: str = ''
    elapsed: Elapsed = Elapsed(min=0.0, max=0.0)
    empty: bool = False


def _proc_result(result: ActionResult, tap):
    if not isinstance(result, ActionResult):
        return
    check = result.test.check
    opts = result.test.options.dict
    message = (
        result.message if isinstance(result, ActionResult) else result.note
    )
    should_check = (
        not check.empty and all(
            opts[k] == check.when[k]
            for k in set(opts.keys()).intersection(check.when.keys())
        ) if opts else True
    )
    if should_check:
        tap.eq_ok(result.success, check.success, check.tap_description)
        if not result.success == check.success:
            tap.note(message)
        if check.description:
            tap.in_ok(
                check.description, result.description, check.tap_description
            )
        if check.message:
            tap.in_ok(check.message, message, check.tap_description)
        if check.elapsed.min:
            assert isinstance(result, ActionResult)
            min = check.elapsed.min - config.TIME_PRECISION
            success = result.elapsed > min
            tap.ok(success, check.tap_description)
            if not success:
                tap.note(
                    'Elapsed min failed with error.'
                    f' Result elapsed "{result.elapsed:.6f}"'
                    f' should be greater then "{min:.6f}".'
                )
        if check.elapsed.max:
            assert isinstance(result, ActionResult)
            max = check.elapsed.max + config.TIME_PRECISION
            success = result.elapsed < max
            tap.ok(success, check.tap_description)
            if not success:
                tap.note(
                    'Elapsed max failed with error.'
                    f' Result elapsed "{result.elapsed:.6f}"'
                    f' should be lesser then "{max:.6f}".'
                )


def check_with_yml(tests: YmlFile, plugin: str = '') -> str:
    """Do the check with the _inner_test directive."""
    tap = Tap()
    results = tests.loop()
    if plugin:
        tap.note(f'--- {plugin} plugin ---')
    results_accum: t.List[Note, Results] = []
    for result in results:
        results_accum.append(result)
        if isinstance(result, Results):
            for r in result.list:
                assert isinstance(r, TapResult), type(result)
                if type(r) in [ActionResult]:
                    _proc_result(r, tap)
        else:
            assert isinstance(result, TapResult), type(result)
            if type(result) in [ActionResult]:
                _proc_result(result, tap)

    left = len(list(tests.file.subtests)) - len(results_accum)
    if left > 0:
        tap.note(
            f'The last {left} test results'
            f' in file {tests.file.name} was not checked'
        )
    print('# Tap output:')
    tap_out = '\n'.join([r.as_tap() for r in results_accum])
    print(intent_tap(tap_out))
    tap()
    return tap_out


def create_folder(path: str, cli_options: dict={}) -> Folder:
    return Folder(
        path=path,
        cli_options={
            'screenshots': {'before': 'none', 'after': 'none'},
            **cli_options
        }
    )


def intent_tap(tap_message: str) -> str:
    return '\n'.join([f'# {l}' for l in tap_message.split('\n')])
