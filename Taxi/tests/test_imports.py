import unittest


class TestImports(unittest.TestCase):

    def test_backend_cpp(self):
        try:
            import taxi_ml_cxx.backend_cpp
            backend_cpp_imported = True
        except ImportError:
            backend_cpp_imported = False
        self.assertTrue(backend_cpp_imported)

    def test_pymlaas(self):
        try:
            import taxi_ml_cxx.pymlaas
            pymlaas_imported = True
        except ImportError:
            pymlaas_imported = False
        self.assertTrue(pymlaas_imported)


if __name__ == '__main__':
    unittest.main()
