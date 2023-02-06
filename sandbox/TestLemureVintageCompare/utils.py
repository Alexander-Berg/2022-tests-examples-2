import re


def get_color_diffs_from_file(f):

    result = {}
    color_re = re.compile(r'diff\s+type\s+is\s+(\w+)')
    excluded_color = ['WHITE']

    with open(f) as F:
        lines = F.read().splitlines()
        color = ""

        for l in lines:
            match = color_re.search(l)
            if match:
                color = match.group(1)
                if color not in excluded_color:
                    result[color] = []
            elif (
                color
                and color not in excluded_color
                and not re.match(r'^\s*$', l)
            ):
                result[color].append(l)

    for k in result.keys():
        if not result[k]:
            del result[k]

    return result
