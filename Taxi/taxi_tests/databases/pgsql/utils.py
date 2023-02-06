import os.path

PLUGIN_DIR = os.path.dirname(__file__)
CONFIGS_DIR = os.path.join(PLUGIN_DIR, 'configs')
SCRIPTS_DIR = os.path.join(PLUGIN_DIR, 'scripts')


def scan_sql_directory(root):
    result = []
    for child in sorted(os.listdir(root)):
        fullpath = os.path.join(root, child)
        if child.endswith('.sql') and os.path.isfile(fullpath):
            result.append(fullpath)
    return result
