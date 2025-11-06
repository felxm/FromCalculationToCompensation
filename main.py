# main.py

import argparse
from steuer_berechner import berechne_steuer
from decimal import Decimal

def format_currency(wert):
    return f"{wert:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def print_ergebnis(ergebnis):
    print("Ergebnis")
    print(f"{'Beschreibung':<55} {'Fünftel-Regelung':>20}    {'Regelbesteuerung':>20}")

    # Ergebnis-Block
    fuenftel = ergebnis['fuenftel']
    regel = ergebnis['regel']

    print(f"{'Einkommensteuer':<55} {format_currency(fuenftel['einkommensteuer']):>17} € {format_currency(regel['einkommensteuer']):>17} €")
    print(f"{'Solidaritätszuschlag':<55} {format_currency(fuenftel['soli']):>17} € {format_currency(regel['soli']):>17} €")
    print(f"{'Kirchensteuer':<55} {format_currency(fuenftel['kirchensteuer']):>17} € {format_currency(regel['kirchensteuer']):>17} €")
    print(f"{'Gesamt-Steuer':<55} {format_currency(fuenftel['gesamt_steuer']):>17} € {format_currency(regel['gesamt_steuer']):>17} €")
    print(f"{'Netto nach Steuern (ohne Berücksichtigung Sozialabgaben)':<55} {format_currency(fuenftel['netto']):>17} € {format_currency(regel['netto']):>17} €")
    print(f"{'Vorteil Fünftel-Regelung':<55} {format_currency(fuenftel['vorteil']):>17} € {format_currency(regel['vorteil']):>17} €")

    print("\nBerechnung")
    print(f"{'Beschreibung':<55} {'Fünftel-Regelung':>20}    {'Regelbesteuerung':>20}")

    # Berechnungs-Block
    f_calc = fuenftel['calc']
    r_calc = regel['calc']

    print(f"{'Gesamteinkünfte':<55} {format_currency(f_calc['gesamteinkuenfte']):>17} € {format_currency(r_calc['gesamteinkuenfte']):>17} €")
    print(f"{'Gesamteinkünfte incl. Progression':<55} {format_currency(f_calc['gesamteinkuenfte_prog']):>17} € {format_currency(r_calc['gesamteinkuenfte_prog']):>17} €")
    print(f"{'Einkommensteuersatz gesamt':<55} {format_currency(f_calc['einkommensteuersatz_gesamt']):>16} % {format_currency(r_calc['einkommensteuersatz_gesamt']):>16} %")
    print(f"{'Weitere Einkünfte':<55} {format_currency(f_calc['weitere_einkuenfte']):>17} € {format_currency(r_calc['weitere_einkuenfte']):>17} €")
    print(f"{'Weitere Einkünfte incl. Progression':<55} {format_currency(f_calc['weitere_einkuenfte_prog']):>17} € {format_currency(r_calc['weitere_einkuenfte_prog']):>17} €")
    print(f"{'Einkommensteuersatz sonstige Einkünfte':<55} {format_currency(f_calc['einkommensteuersatz_sonstige']):>16} % {format_currency(r_calc['einkommensteuersatz_sonstige']):>16} %")
    print(f"{'Einkommensteuer sonstige Einkünfte':<55} {format_currency(f_calc['einkommensteuer_sonstige']):>17} € {format_currency(r_calc['einkommensteuer_sonstige']):>17} €")
    print(f"{'Einkommensteuer Fünftel-Regelung':<55} {format_currency(f_calc['einkommensteuer_fuenftel_regelung']):>17} € {format_currency(r_calc['einkommensteuer_fuenftel_regelung']):>17} €")
    print(f"{'Einkommensteuer Gesamt':<55} {format_currency(f_calc['einkommensteuer_gesamt']):>17} € {format_currency(r_calc['einkommensteuer_gesamt']):>17} €")
    print(f"{'Solidaritätszuschlag':<55} {format_currency(f_calc['soli']):>17} € {format_currency(r_calc['soli']):>17} €")
    print(f"{'Kirchensteuer':<55} {format_currency(f_calc['kirchensteuer']):>17} € {format_currency(r_calc['kirchensteuer']):>17} €")
    print(f"{'Steuer gesamt':<55} {format_currency(f_calc['steuer_gesamt']):>17} € {format_currency(r_calc['steuer_gesamt']):>17} €")
    print(f"{'Einkommensteuersatz Einmalzahlung':<55} {format_currency(f_calc['einkommensteuersatz_einmalzahlung']):>16} % {format_currency(r_calc['einkommensteuersatz_einmalzahlung']):>16} %")
    print(f"{'Einkommensteuersatz Gesamt':<55} {format_currency(f_calc['einkommensteuersatz_gesamt_unten']):>16} % {format_currency(r_calc['einkommensteuersatz_gesamt_unten']):>16} %")


def main():
    parser = argparse.ArgumentParser(description="Berechnung des deutschen Nettoeinkommens")
    parser.add_argument("--jahr", type=int, default=2025, help="Das Steuerjahr")
    parser.add_argument("--splitting", action="store_true", help="Ob das Splittingverfahren angewendet werden soll")
    parser.add_argument("--kirche", action="store_true", help="Ob Kirchensteuer berücksichtigt werden soll")
    parser.add_argument("--abfindung", type=Decimal, required=True, help="Einmalige Abfindung in Euro")
    parser.add_argument("--zvst-eink", type=Decimal, required=True, help="Zusätzliches zu versteuerndes Einkommen in Euro")
    parser.add_argument("--progr-eink", type=Decimal, default=Decimal('0'), help="Zusätzliches Progressionseinkommen in Euro")

    args = parser.parse_args()

    # Eingaben an die Konsole ausgeben
    print(f"Jahr:           {args.jahr}")
    print(f"Splitting?:     {'Ja' if args.splitting else 'Kein Splitting'}")
    print(f"Kirche:         {'Ja' if args.kirche else 'Keine'}")
    print(f"Abfindung:      {format_currency(args.abfindung)} €")
    print(f"Zvst. Eink.:    {format_currency(args.zvst_eink)} €")
    print(f"Progr.Eink.:     {format_currency(args.progr_eink)} €")
    print("-------------------------------")

    ergebnis = berechne_steuer(
        jahr=args.jahr,
        splitting=args.splitting,
        kirche=args.kirche,
        abfindung=args.abfindung,
        zvst_eink=args.zvst_eink,
        progr_eink=args.progr_eink
    )

    print_ergebnis(ergebnis)

if __name__ == "__main__":
    main()
