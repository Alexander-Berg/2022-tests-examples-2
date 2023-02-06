class TestImport:
    def test_import(self):
        import metrika.pylib.zk_async_worker
        assert metrika.pylib.zk_async_worker.AsyncWorker.__name__ == 'AsyncWorker'
