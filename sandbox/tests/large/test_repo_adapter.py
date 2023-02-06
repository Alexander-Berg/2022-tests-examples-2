import yatest.common

from sandbox.projects.autocheck.lib.core import repo_adapter


class TestArcAdapter(object):
    def test_svn_like_url(self):
        url = 'arcadia:/arc/trunk/arcadia@8478937'
        bare_repo_path = yatest.common.output_path('svn_bare_repo')
        thin_repo_path = yatest.common.output_path('svn_thin_repo')
        adapter_factory = repo_adapter.get_arc_adapter_factory(bare_repo_path, None, None, True)
        with adapter_factory:
            with adapter_factory.make_arc_thin_adapter_factory() as thin_adapter_factory:
                adapter = thin_adapter_factory.make_arc_adapter(thin_repo_path, url, '')
                assert adapter.revision == 8478937
                assert adapter.get_arcadia_url() == '/arc/trunk/arcadia'

    def test_arc_like_url(self):
        url = 'arcadia-arc:/#729a11c1046296b3e039aad76ab779b84d191dfb'
        bare_repo_path = yatest.common.output_path('arc_bare_repo')
        thin_repo_path = yatest.common.output_path('arc_thin_repo')
        adapter_factory = repo_adapter.get_arc_adapter_factory(bare_repo_path, None, None, False)
        with adapter_factory:
            with adapter_factory.make_arc_thin_adapter_factory() as thin_adapter_factory:
                adapter = thin_adapter_factory.make_arc_adapter(thin_repo_path, url, '')
                assert adapter.revision == -1
                assert adapter.get_arcadia_url() == 'arc://arcadia#729a11c1046296b3e039aad76ab779b84d191dfb'
