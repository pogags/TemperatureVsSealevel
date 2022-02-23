import unittest
from globalTemp import *
import os

class TestTemp(unittest.TestCase):

    def testGetData(self):
        file = 'GlobalTempData.csv'
        if(os.path.exists(file) and os.path.isfile(file)):
            os.remove(file)
        get_data_temp()
        self.assertTrue(os.path.exists(file))

    def testCleanData(self):
        file = 'GlobalTempClean.csv'
        if(os.path.exists(file) and os.path.isfile(file)):
            os.remove(file)
        get_data_temp()
        clean_data_temp()
        self.assertTrue(os.path.exists(file))

    def testGetBoth(self):
        file = 'GlobalTempData.csv'
        if(os.path.exists(file) and os.path.isfile(file)):
            os.remove(file)
        file2 = 'GlobalTempClean.csv'
        if(os.path.exists(file2) and os.path.isfile(file2)):
            os.remove(file2)
        get_temp_csv()
        self.assertTrue(os.path.exists(file) and os.path.exists(file2))

    def testArrayYear(self):
        get_temp_csv()
        df, data = create_temp_local()
        self.assertTrue(type(data[0][0]) == int)

    def testArrayTemp(self):
        get_temp_csv()
        df, data = create_temp_local()
        self.assertTrue(type(data[0][1]) == float)

    def testDfArrayLen(self):
        get_temp_csv()
        df, data = create_temp_local()
        self.assertTrue(len(df) == len(data))

if __name__ == "__main__":
    unittest.main()
