import pytest


@pytest.fixture()
def print_sql(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_to_categories
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_to_categories VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_categories
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_categories VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_to_items
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_to_items VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_items
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_items VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_item_data_bases
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_item_data_bases VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_item_data
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_item_data VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_options_bases
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_options_bases VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_options
            ORDER BY hash
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menu_options VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menus
            ORDER BY place_id, id
        """,
        )
        rows = cursor.fetchall()

        text = 'INSERT INTO eats_restapp_menu.menus VALUES'
        for count, row in enumerate(rows):
            if count > 0:
                text += ','
            text += '(' + str(row) + ')'

        print(text)

    return _mock_func
