import pytest

from testsuite.utils import ordered_object

# Checks /admin/products/v1/dimensions POST
# insert new values into layout_items_dimensions table
@pytest.mark.pgsql('grocery_products')
@pytest.mark.parametrize('width,height', [(2, 1)])
async def test_dimensions_post_smoke(
        taxi_grocery_products, pgsql, width, height,
):
    json = {'width': width, 'height': height}

    response = await taxi_grocery_products.post(
        '/admin/products/v1/dimensions', json=json,
    )
    assert response.status_code == 200

    response_json = response.json()
    ordered_object.assert_eq(json, response_json, [''])

    # Check db
    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT width, height
        FROM products.layout_items_dimensions
        WHERE width = {width} AND height = {height};""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == width
    assert data[0][1] == height

    # Check cache
    await taxi_grocery_products.invalidate_caches()
    response = await taxi_grocery_products.post(
        '/admin/products/v1/dimensions/list', json={},
    )
    assert response.status_code == 200
    dimensions = response.json()['dimensions']
    assert len(dimensions) == 1
    ordered_object.assert_eq(json, dimensions[0], [''])


# Checks /admin/products/v1/dimensions POST
# return 409 on existed
@pytest.mark.pgsql('grocery_products', files=['dimensions.sql'])
@pytest.mark.parametrize(
    'width,height,code,message',
    [
        (
            2,
            2,
            'LAYOUT_ITEM_DIMENSIONS_ALREADY_EXISTS',
            'Layout item size (2, 2) already exists',
        ),
    ],
)
async def test_dimensions_post_409(
        taxi_grocery_products, pgsql, width, height, code, message,
):
    await taxi_grocery_products.invalidate_caches()
    json = {'width': width, 'height': height}

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.layout_items_dimensions""",
    )
    records_before = cursor.fetchall()[0][0]

    response = await taxi_grocery_products.post(
        '/admin/products/v1/dimensions', json=json,
    )

    assert response.status_code == 409
    assert response.json()['code'] == code
    assert response.json()['message'] == message

    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.layout_items_dimensions""",
    )
    assert records_before == cursor.fetchall()[0][0]


# Checks /admin/products/v1/dimensions/list POST
# get all values from layout items dimensions cache
@pytest.mark.pgsql('grocery_products', files=['dimensions.sql'])
async def test_dimensions_list_post_smoke(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v1/dimensions/list', json={},
    )
    assert response.status_code == 200
    expected = load_json('dimensions_list_expected.json')

    ordered_object.assert_eq(response.json(), expected, [''])


# Checks /admin/products/v1/dimensions/list POST
# empty cache returns emply list
@pytest.mark.pgsql('grocery_products')
async def test_dimensions_list_post_empty(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v1/dimensions/list', json={},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), {'dimensions': []}, [''])
