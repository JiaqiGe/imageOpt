import unittest
import imageloader


class TestImageLoader(unittest.TestCase):
    def test_resolve_region(self):
        self.assertEquals(imageloader._resolve_region('chicago'), 178248)

    def test_hotels_in_region(self):
        ids = imageloader._hotels_in_region(178248)
        self.assertEquals(len(ids), 669)
        self.assertEquals(ids[0], '3034')


if __name__ == '__main__':
    unittest.main()
