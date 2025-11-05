# test_tax_calculator.py

import unittest
from decimal import Decimal, getcontext
from tax_calculator import calculate_net_income, calculate_severance_tax

getcontext().prec = 10

class TestTaxCalculator(unittest.TestCase):

    def test_net_income_class_1_medium_income(self):
        """ Test case for a medium income in tax class 1. """
        result = calculate_net_income(Decimal('50000'), tax_class=1)
        self.assertEqual(result['deductions']['income_tax'], Decimal('6883'))
        self.assertEqual(result['net_income'], Decimal('33004.5'))

    def test_net_income_class_3_medium_income(self):
        """ Test case for a medium income in tax class 3 (married). """
        result = calculate_net_income(Decimal('50000'), tax_class=3)
        self.assertEqual(result['deductions']['income_tax'], Decimal('2936'))
        self.assertEqual(result['net_income'], Decimal('36951.5'))

    def test_net_income_high_income_soli(self):
        """ Test case for a high income in tax class 1, which should trigger the solidarity surcharge. """
        result = calculate_net_income(Decimal('100000'), tax_class=1)
        self.assertEqual(result['deductions']['income_tax'], Decimal('23581'))
        # 23581 > 19950, so solidarity surcharge applies
        expected_soli = (Decimal('23581') * Decimal('0.055')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['solidarity_surcharge'], expected_soli)

    def test_net_income_church_tax(self):
        """ Test case to verify church tax calculation. """
        result = calculate_net_income(Decimal('50000'), tax_class=1, in_church=True)
        self.assertGreater(result['deductions']['church_tax'], 0)
        expected_church_tax = (result['deductions']['income_tax'] * Decimal('0.09')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['church_tax'], expected_church_tax)

    def test_net_income_low_income(self):
        """ Test case for a low income where income tax should be zero. """
        result = calculate_net_income(Decimal('15000'), tax_class=1)
        self.assertEqual(result['deductions']['income_tax'], Decimal('0'))

    def test_net_income_ss_ceiling(self):
        """ Test case for an income above social security ceilings to verify capping. """
        result = calculate_net_income(Decimal('120000'), tax_class=1)
        # Check if pension contribution is capped at the ceiling (96600 EUR)
        expected_pension = (Decimal('96600') * Decimal('0.093')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['pension_insurance'], expected_pension)
        # Check if health insurance contribution is capped at the ceiling (66150 EUR)
        expected_health = (Decimal('66150') * Decimal('0.0785')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['health_insurance'], expected_health)

    def test_severance_tax_calculation(self):
        """ Test case for the Fünftelregelung calculation. """
        regular_income = Decimal('40000')
        severance_pay = Decimal('10000')
        tax_class = 1
        expected_tax = Decimal('3230')
        self.assertEqual(calculate_severance_tax(regular_income, severance_pay, tax_class), expected_tax)

    def test_soli_on_severance_default(self):
        """ Test that the solidarity surcharge is applied to severance pay by default. """
        result = calculate_net_income(Decimal('100000'), tax_class=1, severance_pay=Decimal('20000'))
        self.assertGreater(result['deductions']['solidarity_surcharge'], 0)
        expected_soli = ((result['deductions']['income_tax'] + result['deductions']['severance_tax']) * Decimal('0.055')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['solidarity_surcharge'], expected_soli)

    def test_soli_on_severance_disabled(self):
        """ Test that the solidarity surcharge is not applied to severance pay when disabled. """
        result = calculate_net_income(Decimal('100000'), tax_class=1, severance_pay=Decimal('20000'), soli_on_severance=False)
        self.assertGreater(result['deductions']['solidarity_surcharge'], 0)
        expected_soli = (result['deductions']['income_tax'] * Decimal('0.055')).quantize(Decimal('0.01'))
        self.assertEqual(result['deductions']['solidarity_surcharge'], expected_soli)


if __name__ == '__main__':
    unittest.main()
