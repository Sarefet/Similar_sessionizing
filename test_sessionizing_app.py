#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import unittest
import pandas as pd
from utils import load_and_process_data, num_sessions, num_unique_visited_sites, median_session_length

class TestSessionizingApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the specified CSV files
        column_names = ["visitor_id", "site_url", "page_view_url", "timestamp"]
        schema = {
            "visitor_id": "category",
            "site_url": "category",
            "page_view_url": "category",
            "timestamp": "int64"
        }
        csv_files = ['input_1.csv', 'input_2.csv', 'input_3.csv']
        cls.df_filtered, _, _ = load_and_process_data(csv_files, column_names, schema)

    def test_num_sessions(self):
        test_cases = {
            'www.s_1.com': 3684,
            'www.s_2.com': 3632,
            'www.s_3.com': 3640,
            'www.s_4.com': 3584,
            'www.s_5.com': 3623,
            'www.s_6.com': 3712,
            'www.s_7.com': 3598,
            'www.s_8.com': 3683,
            'www.s_9.com': 3730,
            'www.s_10.com': 3674
        }
        for site_url, expected in test_cases.items():
            with self.subTest(site_url=site_url):
                result = num_sessions(self.df_filtered, site_url)
                print(f"Num sessions for {site_url}: {result}")
                self.assertAlmostEqual(result, expected, delta=100)

    def test_num_unique_visited_sites(self):
        test_cases = {
            'visitor_1': 3,
            'visitor_2': 2,
            'visitor_3': 2,
            'visitor_4': 4,
            'visitor_5': 4,
            'visitor_6': 1,
            'visitor_7': 3,
            'visitor_8': 3,
            'visitor_9': 2,
            'visitor_10': 4
        }
        for visitor_id, expected in test_cases.items():
            with self.subTest(visitor_id=visitor_id):
                result = num_unique_visited_sites(self.df_filtered, visitor_id)
                print(f"Num unique visited sites for {visitor_id}: {result}")
                self.assertEqual(result, expected)

    def test_median_session_length(self):
        test_cases = {
            'www.s_1.com': 1353.0,
            'www.s_2.com': 1341.5,
            'www.s_3.com': 1392.5,
            'www.s_4.com': 1361.5,
            'www.s_5.com': 1375.0,
            'www.s_6.com': 1374.0,
            'www.s_7.com': 1318.5,
            'www.s_8.com': 1353.0,
            'www.s_9.com': 1326.5,
            'www.s_10.com': 1329.0
        }
        for site_url, expected in test_cases.items():
            with self.subTest(site_url=site_url):
                result = median_session_length(self.df_filtered, site_url)
                print(f"Median session length for {site_url}: {result}")
                self.assertAlmostEqual(result, expected, delta=300)

if __name__ == '__main__':
    unittest.main()

