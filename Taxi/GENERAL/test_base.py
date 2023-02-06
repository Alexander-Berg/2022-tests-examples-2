def test_base(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(tmp_dir, service=base_service)
    dir_comparator(tmp_dir, 'base')
