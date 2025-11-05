# test_tax_calculator.py

import unittest
from decimal import Decimal, getcontext
from steuer_berechner import berechne_steuer

getcontext().prec = 10

class TestSteuerBerechner(unittest.TestCase):

    def test_berechne_steuer_beispiel(self):
        """
        Testet die Steuerberechnung mit den korrigierten Daten.
        Abfindung: 100.000 €, Zvst. Eink.: 0 €
        """
        ergebnis = berechne_steuer(
            jahr=2025,
            splitting=False,
            kirche=False,
            abfindung=Decimal('100000'),
            zvst_eink=Decimal('0'),
            progr_eink=Decimal('0')
        )

        # Überprüfen Sie einen Schlüsselwert aus der Fünftel-Regelung
        self.assertEqual(ergebnis['fuenftel']['einkommensteuer'], Decimal('-8195'))

        # Überprüfen Sie einen Schlüsselwert aus der Regelbesteuerung
        self.assertEqual(ergebnis['regel']['einkommensteuer'], Decimal('-31088'))

if __name__ == '__main__':
    unittest.main()
