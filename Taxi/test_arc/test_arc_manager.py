import os

from arc import components


async def test_init_lib(library_context, patch, loop):
    @patch('pathlib.Path.mkdir')
    def _mkdir(*args, **kwargs):
        pass

    # pylint: disable=protected-access
    assert not library_context.arc._disabled
    async with library_context.arc.make_client() as arc:
        assert arc.arcadia.resolve() == arc.arcadia
        assert str(arc.arcadia.resolve()).startswith('/tmp/tmp'), arc.arcadia
        assert str(arc.arcadia.resolve()).endswith('arcadia'), arc.arcadia

        assert arc.store.resolve() == arc.store
        assert str(arc.store.resolve()).startswith('/tmp/tmp'), arc.store
        assert str(arc.store.resolve()).endswith('store'), arc.store

        assert arc.work_dir.resolve() == arc.work_dir
        assert str(arc.work_dir.resolve()).startswith('/tmp/tmp'), arc.work_dir

        assert arc.branch == 'trunk'
        await arc.try_checkout('dev_1')
        assert arc.branch == 'dev_1'

        async with library_context.arc.make_client() as parc:
            assert arc.work_dir != parc.work_dir
    version = b'arc version 9262935 (2022-03-23) stable'
    # pylint: disable=protected-access
    sec_arc = components._UpdateArc(library_context)
    assert await sec_arc.version() == version
    assert sec_arc.get_local_version() == version
    assert os.path.exists(sec_arc.file_name)
