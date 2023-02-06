import os.path


def scan_sql_directory(root):
    result = []
    for child in sorted(os.listdir(root)):
        fullpath = os.path.join(root, child)
        if child.endswith('.sql') and os.path.isfile(fullpath):
            result.append(fullpath)
    return result
