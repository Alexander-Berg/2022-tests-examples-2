import re


def match_taximeter_version(user_agent):
    match = re.search(r'(\d+\.\d+(?: \(\d+\)))', user_agent)
    if not match:
        raise Exception(f'Invalid User-Agent: `{user_agent}`')
    return match[0]
