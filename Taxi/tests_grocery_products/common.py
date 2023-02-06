def compare_request_and_response(request_id, request_json, response_json):
    for key, value in response_json.items():
        if key == 'id':
            assert value == request_id
        else:
            assert value == request_json[key]


def compare_dimensions(db_value, json):
    assert (
        db_value == '(' + str(json['width']) + ',' + str(json['height']) + ')'
    )


VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME = (
    'virtual_categories_with_subcategories_view_v9'
)
CATEGORY_GROUPS_VIEW_NAME = 'category_groups_view_v4'
