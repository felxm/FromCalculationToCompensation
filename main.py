# main.py

import argparse
from tax_calculator import calculate_net_income
from decimal import Decimal

def main():
    parser = argparse.ArgumentParser(description="Calculate German Net Income")
    parser.add_argument("gross_income", type=Decimal, help="Gross annual income in Euros")
    parser.add_argument("--tax-class", type=int, default=1, choices=range(1, 7), help="Tax class (1-6)")
    parser.add_argument("--church-tax", action="store_true", help="Whether to include church tax")
    parser.add_argument("--severance-pay", type=Decimal, default=Decimal('0'), help="One-time severance payment in Euros")
    parser.add_argument("--no-soli-on-severance", action="store_false", dest="soli_on_severance", help="Disable solidarity surcharge on severance pay")

    args = parser.parse_args()

    result = calculate_net_income(
        gross_income=args.gross_income,
        tax_class=args.tax_class,
        in_church=args.church_tax,
        severance_pay=args.severance_pay,
        soli_on_severance=args.soli_on_severance
    )

    print("\n--- Income and Deductions Breakdown ---")
    print(f"Gross Income: {result['gross_income']:.2f} €")
    if result['severance_pay'] > 0:
        print(f"Severance Pay: {result['severance_pay']:.2f} €")
    print("-" * 30)
    print("Deductions:")
    for key, value in result['deductions'].items():
        print(f"  {key.replace('_', ' ').title()}: {value:.2f} €")
    print("-" * 30)
    print(f"Net Income: {result['net_income']:.2f} €")
    print("---------------------------------------")

if __name__ == "__main__":
    main()
