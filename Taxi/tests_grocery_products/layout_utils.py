from testsuite.utils import ordered_object

from tests_grocery_products import common


def get_expected_recs_count(db, layout_groups, layout_id=None):
    # Let's get total layout_category_groups items count
    # |groups_recs| and target layout category groups
    # items count |target_groups_recs| so we can
    # calculate |expected_groups_recs| to  check further
    # that we haven't delete anything extra
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*) FROM products.layout_category_groups;""",
    )
    groups_recs = cursor.fetchall()[0][0]
    if layout_id:
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT COUNT(*) FROM products.layout_category_groups
            WHERE layout_id = '{layout_id}';""",
        )
        target_groups_recs = cursor.fetchall()[0][0]
    else:
        target_groups_recs = 0
    expected_groups_recs = (
        groups_recs - target_groups_recs + len(layout_groups)
    )

    # Let's get total layout_virtual_categories items count
    # |categories_recs| and target layout virtual categories
    # items count |target_categories_recs| so we can
    # count |expected_categories_recs| to check
    # further that we haven't delete anything extra
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*) FROM products.layout_virtual_categories;""",
    )
    categories_recs = cursor.fetchall()[0][0]
    if layout_id:
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT COUNT(*) FROM products.layout_virtual_categories
            WHERE layout_id = '{layout_id}';""",
        )
        target_categories_recs = cursor.fetchall()[0][0]
    else:
        target_categories_recs = 0
    expected_categories_recs = categories_recs - target_categories_recs
    for category_group in layout_groups:
        expected_categories_recs += len(category_group['categories'])

    return {
        'groups': expected_groups_recs,
        'categories': expected_categories_recs,
    }


def check_layout_category_images_v3(images_data, category_data):
    assert len(images_data) == sum(
        len(image['dimensions']) for image in category_data['images']
    )

    for db_image in images_data:
        found = False
        for image in category_data['images']:
            if db_image[0] == image['id']:
                db_dimensions = [
                    int(i) for i in db_image[1].strip('()').split(',')
                ]
                for dimensions in image['dimensions']:
                    if (
                            db_dimensions[0] == dimensions['width']
                            and db_dimensions[1] == dimensions['height']
                    ):
                        found = True
                        break
            if found:
                break
        assert found


def check_layouts_response(
        db,
        layout_id,
        layouts_request,
        response_data,
        expected_recs_count,
        layout_version,
):
    common.compare_request_and_response(
        layout_id, layouts_request['layout'], response_data['layout'],
    )
    ordered_object.assert_eq(
        layouts_request['structure'],
        response_data['structure'],
        ['groups', 'groups.categories'],
    )
    layout_groups = layouts_request['structure']['groups']

    # Get info about layout_category_groups table
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT category_group_id, image_id, meta, rank
        FROM products.layout_category_groups
        WHERE layout_id = '{layout_id}'
        ORDER BY rank;""",
    )
    data = cursor.fetchall()
    assert len(data) == len(layout_groups)
    for i, group in enumerate(data):
        assert group[0] == layout_groups[i]['group_id']
        assert group[1] == layout_groups[i]['image_id']
        assert group[2] == layout_groups[i]['meta']
        assert group[3] == layout_groups[i]['order']

        # Get info about layout_virtual_categories
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT virtual_category_id, meta, rank
            FROM products.layout_virtual_categories
            WHERE layout_id = '{layout_id}'
            AND category_group_id = '{group[0]}'
            ORDER BY rank;""",
        )
        categories_data = cursor.fetchall()
        expected_data = layout_groups[i]['categories']
        assert len(categories_data) == len(expected_data)
        for j, category in enumerate(categories_data):
            assert category[0] == expected_data[j]['category_id']
            assert category[1] == expected_data[j]['meta']
            assert category[2] == expected_data[j]['order']

            cursor = db.cursor()
            cursor.execute(
                f"""SELECT image_id, dimensions
                FROM products.layout_virtual_categories_images
                WHERE layout_id = '{layout_id}'
                AND category_group_id = '{group[0]}'
                AND virtual_category_id = '{category[0]}'
                ORDER BY image_id, dimensions;""",
            )
            images_data = cursor.fetchall()
            if layout_version == 'v3':
                check_layout_category_images_v3(images_data, expected_data[j])
            else:
                assert False

    # Now let's check that we haven't delete anything extra
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*) FROM products.layout_category_groups;""",
    )
    assert cursor.fetchall()[0][0] == expected_recs_count['groups']

    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*) FROM products.layout_virtual_categories;""",
    )
    assert cursor.fetchall()[0][0] == expected_recs_count['categories']


def get_layouts_count(db):
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.layouts""",
    )
    return cursor.fetchall()[0][0]


def check_layouts_count(db, expected):
    assert expected == get_layouts_count(db)


def check_status(db, layout_id, status):
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT status
            FROM products.layouts
            WHERE id = '{layout_id}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == status
