from typing import List


def juggler_raw_event(
        host: str, description: str, service: str, status: str,
) -> dict:
    return {
        'description': description,
        'host': host,
        'service': service,
        'status': status,
        'instance': '',
        'tags': [],
    }


def juggler_requests(
        *events, source: str = 'taxi-billing-audit',
) -> List[dict]:
    return [{'source': source, 'events': list(events)}]


def no_juggler_requests() -> List[dict]:
    return []
