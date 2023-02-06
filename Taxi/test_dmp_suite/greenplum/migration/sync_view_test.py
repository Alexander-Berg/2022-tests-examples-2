import pytest
from mock import patch

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
    Int,
    String,
    resolve_meta,
)
from dmp_suite.greenplum import migration
from dmp_suite.greenplum.view import View
from test_dmp_suite.greenplum import utils
from .utils import (
    create,
    run_migration_in_same_process,
    assert_real_field_type,
    assert_no_field_in_db,
)


def get_real_grants(view_cls):
    meta = resolve_meta(view_cls)
    grants = gp.connection.get_privileges(meta.schema, meta.table_name)
    return grants


class SyncViewTable(GPTable):
    __layout__ = utils.TestLayout(name='example_table')

    a = Int()
    b = Int()
    c = Int()


@pytest.mark.slow('gp')
def test_sync_view_should_create_view_if_it_does_not_exist():
    # Проверим как сработает добавление вью
    with gp.connection.transaction():
        class TheTable(GPTable):
            __layout__ = utils.TestLayout(name='example_table')

            a = Int()

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': TheTable}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        create(TheTable)

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        assert_real_field_type(NewView, 'a', 'integer')


@pytest.mark.slow('gp')
def test_sync_view_should_recreate_dependent_views(generate_new_taxidwh_run_id):
    # Проверим как сработает добавление во вью колонки если от View зависят несколько других.
    # Зависимости идут по цепочке:
    # TheTable -> ViewBefore -> DependentView1 -> DependentView2
    # и мы меняем ViewBefore на ViewAfter
    with gp.connection.transaction():
        class TheTable(GPTable):
            __layout__ = utils.TestLayout(name='example_table')

            a = Int()

        class ViewBefore(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': TheTable}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        class DependentView1(View):
            __layout__ = utils.TestLayout(name='dep_view1')
            __tables__ = {'base': ViewBefore}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        class DependentView2(View):
            __layout__ = utils.TestLayout(name='dep_view2')
            __tables__ = {'base': DependentView1}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        class ViewAfter(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': TheTable}
            __query__ = 'SELECT a, a+1 as b FROM {base}'

            a = Int()
            b = Int()

        create(TheTable)

        # Сначала создадим цепочку View
        for view in (ViewBefore, DependentView1, DependentView2):
            generate_new_taxidwh_run_id()
            task = migration.sync_view(view)
            run_migration_in_same_process(task)

        # Убедимся, что у колонки b пока нет:
        assert_no_field_in_db(ViewAfter, 'b')
        # и у пользователя 'etl' должны быть гранты
        grants = get_real_grants(DependentView2)
        assert 'etl' in grants

        # А теперь попробуем пересоздать view
        generate_new_taxidwh_run_id()
        task = migration.sync_view(ViewAfter)
        run_migration_in_same_process(task)

        # Убедимся, что у неё появилась новая колонка
        assert_real_field_type(ViewAfter, 'b', 'integer')

        # И проверим, что зависимые вьюхи всё ещё существуют
        assert_real_field_type(DependentView1, 'a', 'integer')
        assert_real_field_type(DependentView2, 'a', 'integer')

        # Так же, убедимся, что сохранились гранты на зависимых вьюхах
        grants = get_real_grants(DependentView2)
        assert 'etl' in grants


@pytest.mark.slow('gp')
def test_sync_view_should_fail_if_no_grants(generate_new_taxidwh_run_id):
    # Проверим что таск упадёт, если выполняется от имени пользовавтеля, у которого нет грантов, чтобы
    # Пересоздать зависимую view.
    # Для этого, создадим цепочку:
    # TheTable -> ViewBefore -> DependentView
    # выдадим грант ALL на ViewBefore пользователю etl
    # а потом попробуем её пересоздать от его имени.
    #
    # Ожидается, что таск не должен ничего поменять, потому что
    # у etl нет прав менять DependentView
    with gp.connection.transaction():
        class TheTable(GPTable):
            __layout__ = utils.TestLayout(name='example_table')

            a = Int()

        class ViewBefore(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': TheTable}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        class DependentView(View):
            __layout__ = utils.TestLayout(name='dep_view')
            __tables__ = {'base': ViewBefore}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        class ViewAfter(ViewBefore):
            __query__ = 'SELECT a+1 as b, a FROM {base}'  # change field order to force recreation

            a = Int()
            b = Int()

        create(TheTable)

        # Сначала создадим цепочку View
        for view in (ViewBefore, DependentView):
            generate_new_taxidwh_run_id()
            task = migration.sync_view(view)
            run_migration_in_same_process(task)

        # Попробуем пересоздать view, прикинувшись, что прав дочернюю вью у нас нет.:
        original_get_privileges = gp.connection.get_privileges

        def fake_get_privileges(schema, name):
            if (
                    schema == DependentView.get_schema() and
                    name == DependentView.get_view_name()
            ):
                return {'etl': {'INSERT', 'UPDATE', 'DELETE'}}
            return original_get_privileges(schema, name)

        with patch.object(gp.connection, 'get_privileges', new=fake_get_privileges):
            generate_new_taxidwh_run_id()

            task = migration.sync_view(ViewAfter)

            with pytest.raises(
                    RuntimeError,
                    match='(?s).*you need to ask help from these people.*testing.dep_view.*: etl'):

                run_migration_in_same_process(task)

        # Убедимся, что колонка не появилась
        assert_no_field_in_db(ViewAfter, 'b')


@pytest.mark.slow('gp')
def test_sync_view_new_field():
    with gp.connection.transaction():

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        create(SyncViewTable)

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a, c FROM {base}'

            a = Int()
            c = Int()

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a, c, b FROM {base}'

            a = Int()
            b = Int()
            c = Int()

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)


@pytest.mark.slow('gp')
def test_sync_view_change_order():
    with gp.connection.transaction():
        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a FROM {base}'

            a = Int()

        create(SyncViewTable)

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT b, a FROM {base}'

            a = Int()
            b = Int()

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        assert_real_field_type(NewView, 'a', 'integer')
        assert_real_field_type(NewView, 'b', 'integer')


@pytest.mark.slow('gp')
def test_sync_view_change_type():
    with gp.connection.transaction():
        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a,b FROM {base}'

            a = Int()
            b = Int()

        create(SyncViewTable)

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        class NewView(View):
            __layout__ = utils.TestLayout(name='example_view')
            __tables__ = {'base': SyncViewTable}
            __query__ = 'SELECT a, b FROM {base}'

            a = Int()
            b = String()
            c = Int()

        task = migration.sync_view(NewView)
        run_migration_in_same_process(task)

        assert_real_field_type(NewView, 'a', 'integer')
        assert_real_field_type(NewView, 'b', 'character varying')
