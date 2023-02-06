import pathlib

import context.settings

CONFIG_EXTENSIONS_WHITELIST = ['yaml', 'yml']


def valid_config_file(file_path: pathlib.Path):
    return (
        file_path.is_file()
        and (
            file_path.suffix.lstrip('.') in CONFIG_EXTENSIONS_WHITELIST
        )
    )


def path_is_relative_to(path, parent):
    # TODO DMPDEV-4193 use pathlib.Path.is_relative_to
    return parent in path.parents


def test_no_local_configs(inside_ci):
    if not inside_ci:
        # local configs are allowed for local development
        return

    config_path = pathlib.Path(context.settings.local_settings())
    local_path = config_path / 'local'
    templates_path = local_path / 'templates'
    local_configs = []
    for path in local_path.rglob('*'):
        if path.is_file():
            # templates are allowed
            if not path_is_relative_to(path, templates_path):
                if valid_config_file(path):
                    local_configs.append(path)

    msg = (
        f'Local config files: {", ".join(str(f) for f in local_configs)}. '
        'Make sure not to commit these files'
    )
    assert not local_configs, msg
