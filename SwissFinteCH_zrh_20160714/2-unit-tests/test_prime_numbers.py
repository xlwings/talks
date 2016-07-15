import os
import unittest
import xlwings as xw

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestPrime(unittest.TestCase):
    def setUp(self):
        xl_file = os.path.join(this_dir, 'prime_numbers.xlsm')
        self.wb = xw.Workbook(xl_file)

        # Map functions
        self.is_prime = self.wb.macro('Module1.is_prime')

    def test_negative(self):
        self.assertFalse(self.is_prime(-5))

    def test_zero(self):
        self.assertFalse(self.is_prime(0))

    def test_100(self):
        """Tests all number numbers from 1 to 100, taken from https://en.wikipedia.org/wiki/Prime_number"""
        prime_numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        for n in range(1, 101):
            if n in prime_numbers:
                self.assertTrue(self.is_prime(n))
            else:
                self.assertFalse(self.is_prime(n))

    @staticmethod
    def is_prime2(number):
        """Alternative implementation of the VBA function"""
        if number <= 1:
            return False

        for i in range(2, number):
            if number % i == 0:
                return False

        return True

    def test_100_alternative(self):
        """Compare the VBA implementation with an alternative implementation in Python"""
        for n in range(1, 101):
            self.assertEqual(self.is_prime(n), self.is_prime2(n))


if __name__ == '__main__':
    unittest.main()
