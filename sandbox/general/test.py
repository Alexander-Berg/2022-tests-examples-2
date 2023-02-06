import unittest
import checker


class TestFixies(unittest.TestCase):

    def test_03_47_prod(self):
        res = checker.fix_thumb_url_03_47("//im0-tub-ru.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")
        self.assertEqual(res, "//im4-tub-ru.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")

    def test_03_47_test(self):
        res = checker.fix_thumb_url_03_47("//im5-tub-ru.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")
        self.assertEqual(res, "//im1-tub-ru.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")

    def test_03_imtub_test_05(self):
        res = checker.fix_thumb_url_03_imtub_test("//im5-tub-tr.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")
        self.assertEqual(res, "//im5-tub-tr.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")

    def test_03_imtub_test_prod(self):
        res = checker.fix_thumb_url_03_imtub_test("//im3-tub-tr.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")
        self.assertEqual(res, "//imtub-test.search.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")

    def test_03_imtub_test_test(self):
        res = checker.fix_thumb_url_03_imtub_test("//imtub-test.search.yandex.net/i?id=6dd6e9510d529cc291be9dc0827b88a7")
        self.assertRegexpMatches(res, "//im[0-3]-tub-ru\.yandex\.net/i\?id=6dd6e9510d529cc291be9dc0827b88a7")


if __name__ == '__main__':
    unittest.main()
