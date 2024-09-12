import unittest
from src.scraping.scrapers.jinbocho_theater.scrape_programs import extract_date

class TestExtractDate(unittest.TestCase):
    
    def test_extract_valid_date(self):
        pattern = r"(\d+)年(\d+)月(\d+)日"
        text = "2024年09月12日"
        expected = ('2024', '09', '12')
        self.assertEqual(extract_date(pattern, text), expected)

    def test_extract_invalid_date(self):
        pattern = r"(\d+)年(\d+)月(\d+)日"
        text = "日付は記載されていません"
        self.assertIsNone(extract_date(pattern, text))

if __name__ == '__main__':
    unittest.main()
