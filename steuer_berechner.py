# tax_calculator.py

from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 10

# Social security contribution rates for 2024 (employee's share)
PENSION_INSURANCE_RATE = Decimal('0.093')
UNEMPLOYMENT_INSURANCE_RATE = Decimal('0.013')
HEALTH_INSURANCE_RATE = Decimal('0.0785') # General rate, can vary
CARE_INSURANCE_RATE = Decimal('0.01775')

# Social security contribution ceilings for 2025
PENSION_CEILING = Decimal('96600')
HEALTH_CARE_CEILING = Decimal('66150')

# Solidarity surcharge rate
SOLIDARITY_SURCHARGE_RATE = Decimal('0.055')
SOLIDARITY_SURCHARGE_FREI_SINGLE = Decimal('19950')
SOLIDARITY_SURCHARGE_FREI_MARRIED = Decimal('39900')

# Church tax rate
CHURCH_TAX_RATE = Decimal('0.09') # Varies by state (8% or 9%)

def calculate_income_tax(taxable_income, tax_class):
    """
    Calculates the income tax based on the 2025 progressive tax formula.
    """
    taxable_income = Decimal(taxable_income)

    # Use Splittingtabelle for married couples (tax classes 3 and 4)
    if tax_class in [3, 4]:
        taxable_income /= 2

    gfb = Decimal('12096') # Grundfreibetrag (basic tax-free allowance)

    if taxable_income <= gfb:
        tax = Decimal('0')
    elif taxable_income <= Decimal('17443'):
        y = (taxable_income - gfb) / Decimal('10000')
        tax = (Decimal('932.30') * y + Decimal('1400')) * y
    elif taxable_income <= Decimal('68480'):
        y = (taxable_income - Decimal('17443')) / Decimal('10000')
        tax = (Decimal('176.64') * y + Decimal('2397')) * y + Decimal('1015.13')
    elif taxable_income <= Decimal('277825'):
        tax = taxable_income * Decimal('0.42') - Decimal('10911.92')
    else:
        tax = taxable_income * Decimal('0.45') - Decimal('19246.67')

    tax = tax.to_integral_value(rounding='ROUND_DOWN')

    if tax_class in [3, 4]:
        tax *= 2

    return tax

def calculate_severance_tax(regular_income, severance_pay, tax_class):
    """
    Calculates the tax on severance pay using the Fünftelregelung (one-fifth rule).
    """
    tax_on_regular_income = calculate_income_tax(regular_income, tax_class)
    tax_on_regular_income_plus_one_fifth = calculate_income_tax(regular_income + (severance_pay / 5), tax_class)
    tax_on_severance = (tax_on_regular_income_plus_one_fifth - tax_on_regular_income) * 5
    return tax_on_severance

def calculate_net_income(gross_income, tax_class=1, in_church=False, severance_pay=Decimal('0'), soli_on_severance=True):
    """
    Calculates the net income after all deductions.
    """
    gross_income = Decimal(gross_income)

    # Standard deductibles
    arbeitnehmer_pauschbetrag = Decimal('1230')
    sonderausgaben_pauschbetrag = Decimal('36')

    # Social security contributions
    pension_insurance = (min(gross_income, PENSION_CEILING) * PENSION_INSURANCE_RATE).quantize(Decimal('0.01'))
    unemployment_insurance = (min(gross_income, PENSION_CEILING) * UNEMPLOYMENT_INSURANCE_RATE).quantize(Decimal('0.01'))
    health_insurance = (min(gross_income, HEALTH_CARE_CEILING) * HEALTH_INSURANCE_RATE).quantize(Decimal('0.01'))
    care_insurance = (min(gross_income, HEALTH_CARE_CEILING) * CARE_INSURANCE_RATE).quantize(Decimal('0.01'))

    social_security_total = pension_insurance + unemployment_insurance + health_insurance + care_insurance

    taxable_income = gross_income - arbeitnehmer_pauschbetrag - sonderausgaben_pauschbetrag - social_security_total

    if taxable_income < 0:
        taxable_income = Decimal('0')

    income_tax = calculate_income_tax(taxable_income, tax_class)

    # Calculate tax on severance pay
    severance_tax = Decimal('0')
    if severance_pay > 0:
        severance_tax = calculate_severance_tax(taxable_income, severance_pay, tax_class)

    # Calculate solidarity surcharge
    solidarity_surcharge = Decimal('0')
    freigrenze = SOLIDARITY_SURCHARGE_FREI_MARRIED if tax_class in [3, 4] else SOLIDARITY_SURCHARGE_FREI_SINGLE
    total_tax = income_tax
    if soli_on_severance:
        total_tax += severance_tax

    if total_tax > freigrenze:
        solidarity_surcharge = (total_tax * SOLIDARITY_SURCHARGE_RATE).quantize(Decimal('0.01'))

    # Calculate church tax
    church_tax = Decimal('0')
    if in_church:
        church_tax = (income_tax * CHURCH_TAX_RATE).quantize(Decimal('0.01'))

    # Calculate total deductions
    total_deductions = income_tax + social_security_total + solidarity_surcharge + church_tax + severance_tax

    # Calculate net income
    net_income = gross_income + severance_pay - total_deductions

    return {
        "gross_income": gross_income,
        "net_income": net_income,
        "severance_pay": severance_pay,
        "deductions": {
            "income_tax": income_tax,
            "pension_insurance": pension_insurance,
            "unemployment_insurance": unemployment_insurance,
            "health_insurance": health_insurance,
            "care_insurance": care_insurance,
            "solidarity_surcharge": solidarity_surcharge,
            "church_tax": church_tax,
            "severance_tax": severance_tax,
            "total_deductions": total_deductions
        }
    }
