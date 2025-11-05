# test_tax_calculator.py

import unittest
from decimal import Decimal, getcontext
from steuer_berechner import berechne_steuer

getcontext().prec = 10

class TestSteuerBerechner(unittest.TestCase):

    def test_berechne_steuer_100k_abfindung(self):
        """
        Testet die Steuerberechnung mit 100.000 € Abfindung.
        """
        ergebnis = berechne_steuer(
            jahr=2025,
            splitting=False,
            kirche=False,
            abfindung=Decimal('100000'),
            zvst_eink=Decimal('0'),
            progr_eink=Decimal('0')
        )

        self.assertEqual(ergebnis['fuenftel']['einkommensteuer'], Decimal('-8195'))
        self.assertEqual(ergebnis['regel']['einkommensteuer'], Decimal('-31088'))

    def test_berechne_steuer_200k_abfindung_mit_soli(self):
        """
        Testet die Steuerberechnung mit 200.000 € Abfindung und überprüft den Soli.
        """
        ergebnis = berechne_steuer(
            jahr=2025,
            splitting=False,
            kirche=False,
            abfindung=Decimal('200000'),
            zvst_eink=Decimal('0'),
            progr_eink=Decimal('0')
        )

        # Test Fünftel-Regelung
        self.assertEqual(ergebnis['fuenftel']['einkommensteuer'], Decimal('-36600'))
        self.assertEqual(ergebnis['fuenftel']['soli'], Decimal('-1981.35'))

        # Test Regelbesteuerung
        self.assertEqual(ergebnis['regel']['einkommensteuer'], Decimal('-73088'))
        self.assertEqual(ergebnis['regel']['soli'], Decimal('-4019.84'))

if __name__ == '__main__':
    unittest.main()
