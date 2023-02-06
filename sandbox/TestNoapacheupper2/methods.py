# !/usr/bin/env python3


def xpath_get(json, path):
    current_subtree = json
    try:
        for x in path.strip("/").split("/"):
            if isinstance(current_subtree, dict):
                current_subtree = current_subtree.get(x)
            elif isinstance(current_subtree, list):
                current_subtree = current_subtree[int(x)]
    except:
        return None
        # pass

    return current_subtree


def _is_market_wizard(data):
    return [xpath_get(data, 'searchdata.docs_right/0/construct/0/counter')]


# the same above
def _is_company_wizard(data):
    return [xpath_get(data, 'searchdata.docs_right/0/construct/0/counter_prefix')]
