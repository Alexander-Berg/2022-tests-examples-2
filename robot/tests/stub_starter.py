
SAAS_INFO_RESPONSE = {
    "SentCount": 4045364019,
    "service_info": {
        "name": "smelter_saas",
        "type": "stable"
    },
    "WordCount": 48578482101,
    "KPS": {
        "123": 942942177
    }
}


def empty_search(search_request):
    return []


def non_empty_search(search_request):
    for i in range(search_request.get("docs_per_page", 20)):
        yield {
            "Url": f"https://urlfromsaas{i%5}/somepath{i}",
            "Snippet": f"some random {i} snippet"
        }


def empty_delete(channel_id):
    return True


def get_saas_info():
    return SAAS_INFO_RESPONSE
