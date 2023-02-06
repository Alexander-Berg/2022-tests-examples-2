import pathlib


def substitute_paths(arc_calls, substitute_dict):
    for arc_call in arc_calls:
        arc_call['args'] = [
            replace_paths(arg, substitute_dict) for arg in arc_call['args']
        ]
        arc_call['kwargs']['cwd'] = pathlib.PosixPath(
            replace_paths(arc_call['kwargs']['cwd'], substitute_dict),
        )


def replace_paths(text, substitute_dict):
    for key, dir_name in substitute_dict.items():
        text = text.replace(f'${key}', str(dir_name))
    return text
