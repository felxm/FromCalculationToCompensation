# steuer_berechner.py

from decimal import Decimal, getcontext

# Präzision für Dezimalberechnungen festlegen
getcontext().prec = 10

# Konstanten
SOLIDARITATSZUSCHLAG_SATZ = Decimal('0.055')
KIRCHENSTEUER_SATZ = Decimal('0.09') # Annahme für die meisten Bundesländer

def _berechne_einkommensteuer_basis(zu_versteuerndes_einkommen, splitting):
    """
    Berechnet die Einkommensteuer nach der progressiven Steuerformel für 2025.
    """
    zve = Decimal(zu_versteuerndes_einkommen)
    if zve < 0: zve = Decimal('0')

    if splitting:
        zve /= 2

    gfb = Decimal('12096')

    if zve <= gfb:
        steuer = Decimal('0')
    elif zve <= Decimal('17443'):
        y = (zve - gfb) / Decimal('10000')
        steuer = (Decimal('932.30') * y + Decimal('1400')) * y
    elif zve <= Decimal('68480'):
        y = (zve - Decimal('17443')) / Decimal('10000')
        steuer = (Decimal('176.64') * y + Decimal('2397')) * y + Decimal('1015.13')
    elif zve <= Decimal('277825'):
        steuer = zve * Decimal('0.42') - Decimal('10911.92')
    else:
        steuer = zve * Decimal('0.45') - Decimal('19246.67')

    steuer = steuer.to_integral_value(rounding='ROUND_DOWN')

    if splitting:
        steuer *= 2

    return steuer

def _berechne_einkommensteuer_mit_progression(zv_eink, progr_eink, splitting):
    """
    Berechnet die Einkommensteuer unter Berücksichtigung des Progressionsvorbehalts.
    """
    if zv_eink <= 0:
        return Decimal('0')

    bemessungsgrundlage_fuer_satz = zv_eink + progr_eink
    steuer_fuer_satz = _berechne_einkommensteuer_basis(bemessungsgrundlage_fuer_satz, splitting)

    if bemessungsgrundlage_fuer_satz <= 0:
        return Decimal('0')

    durchschnittssteuersatz = steuer_fuer_satz / bemessungsgrundlage_fuer_satz

    return (zv_eink * durchschnittssteuersatz).to_integral_value(rounding='ROUND_DOWN')


def _berechne_soli(einkommensteuer, splitting):
    """
    Berechnet den Solidaritätszuschlag unter Berücksichtigung der Freigrenze und Milderungszone.
    """
    freigrenze = Decimal('39900') if splitting else Decimal('19950')
    if einkommensteuer <= freigrenze:
        return Decimal('0')

    soli_milderung = (einkommensteuer - freigrenze) * Decimal('0.119')
    soli_voll = einkommensteuer * SOLIDARITATSZUSCHLAG_SATZ
    return min(soli_milderung, soli_voll).quantize(Decimal('0.01'))


def berechne_steuer(jahr, splitting, kirche, abfindung, zvst_eink, progr_eink):
    abfindung = Decimal(abfindung)
    zvst_eink = Decimal(zvst_eink)
    progr_eink = Decimal(progr_eink)

    # --- Regelbesteuerung ---
    regel_gesamteinkuenfte = zvst_eink + abfindung
    regel_einkommensteuer = _berechne_einkommensteuer_mit_progression(regel_gesamteinkuenfte, progr_eink, splitting)
    regel_soli = _berechne_soli(regel_einkommensteuer, splitting)
    regel_kirchensteuer = (regel_einkommensteuer * KIRCHENSTEUER_SATZ).quantize(Decimal('0.01')) if kirche else Decimal('0')
    regel_gesamt_steuer = regel_einkommensteuer + regel_soli + regel_kirchensteuer
    regel_netto = regel_gesamteinkuenfte - regel_gesamt_steuer

    # --- Fünftel-Regelung ---
    est_auf_zvst_eink = _berechne_einkommensteuer_mit_progression(zvst_eink, progr_eink, splitting)

    fuenftel_basis = zvst_eink + (abfindung / 5)
    est_auf_fuenftel_basis = _berechne_einkommensteuer_mit_progression(fuenftel_basis, progr_eink, splitting)

    mehrsteuer_durch_fuenftel = est_auf_fuenftel_basis - est_auf_zvst_eink
    fuenftel_einkommensteuer_abfindung = mehrsteuer_durch_fuenftel * 5
    fuenftel_einkommensteuer_gesamt = est_auf_zvst_eink + fuenftel_einkommensteuer_abfindung

    fuenftel_soli = _berechne_soli(fuenftel_einkommensteuer_gesamt, splitting)
    fuenftel_kirchensteuer = (fuenftel_einkommensteuer_gesamt * KIRCHENSTEUER_SATZ).quantize(Decimal('0.01')) if kirche else Decimal('0')
    fuenftel_gesamt_steuer = fuenftel_einkommensteuer_gesamt + fuenftel_soli + fuenftel_kirchensteuer
    fuenftel_netto = zvst_eink + abfindung - fuenftel_gesamt_steuer
    vorteil_fuenftel = regel_gesamt_steuer - fuenftel_gesamt_steuer

    # --- Kennzahlen für Ausgabe ---
    # Regelbesteuerung
    regel_calc = {
        "gesamteinkuenfte": regel_gesamteinkuenfte, "gesamteinkuenfte_prog": regel_gesamteinkuenfte + progr_eink,
        "einkommensteuersatz_gesamt": (regel_einkommensteuer / regel_gesamteinkuenfte * 100) if regel_gesamteinkuenfte > 0 else Decimal('0'),
        "weitere_einkuenfte": zvst_eink, "weitere_einkuenfte_prog": zvst_eink + progr_eink,
        "einkommensteuersatz_sonstige": (_berechne_einkommensteuer_basis(zvst_eink + progr_eink, splitting) / (zvst_eink + progr_eink) * 100) if (zvst_eink + progr_eink) > 0 else Decimal('0'),
        "einkommensteuer_sonstige": -est_auf_zvst_eink,
        "einkommensteuer_gesamt": -regel_einkommensteuer, "soli": -regel_soli, "kirchensteuer": -regel_kirchensteuer,
        "steuer_gesamt": -regel_gesamt_steuer, "einkommensteuersatz_gesamt_unten": (regel_gesamt_steuer / regel_gesamteinkuenfte * 100) if regel_gesamteinkuenfte > 0 else Decimal('0'),
        "einkommensteuer_fuenftel_regelung": Decimal('0'), "einkommensteuersatz_einmalzahlung": Decimal('0'),
    }

    # Fünftel-Regelung
    fuenftel_calc = {
        "gesamteinkuenfte": zvst_eink + (abfindung / 5), "gesamteinkuenfte_prog": zvst_eink + (abfindung / 5) + progr_eink,
        "einkommensteuersatz_gesamt": (_berechne_einkommensteuer_basis(zvst_eink + (abfindung/5) + progr_eink, splitting) / (zvst_eink + (abfindung/5) + progr_eink) * 100) if (zvst_eink + (abfindung/5) + progr_eink) > 0 else Decimal('0'),
        "weitere_einkuenfte": zvst_eink, "weitere_einkuenfte_prog": zvst_eink + progr_eink,
        "einkommensteuersatz_sonstige": regel_calc["einkommensteuersatz_sonstige"],
        "einkommensteuer_sonstige": -est_auf_zvst_eink,
        "einkommensteuer_fuenftel_regelung": -fuenftel_einkommensteuer_abfindung,
        "einkommensteuer_gesamt": -fuenftel_einkommensteuer_gesamt, "soli": -fuenftel_soli, "kirchensteuer": -fuenftel_kirchensteuer,
        "steuer_gesamt": -fuenftel_gesamt_steuer,
        "einkommensteuersatz_einmalzahlung": (fuenftel_einkommensteuer_abfindung / abfindung * 100) if abfindung > 0 else Decimal('0'),
        "einkommensteuersatz_gesamt_unten": (fuenftel_gesamt_steuer / (zvst_eink + abfindung) * 100) if (zvst_eink + abfindung) > 0 else Decimal('0'),
    }

    return {
        "fuenftel": {"einkommensteuer": -fuenftel_einkommensteuer_gesamt, "soli": -fuenftel_soli, "kirchensteuer": -fuenftel_kirchensteuer, "gesamt_steuer": -fuenftel_gesamt_steuer, "netto": fuenftel_netto, "vorteil": vorteil_fuenftel, "calc": fuenftel_calc},
        "regel": {"einkommensteuer": -regel_einkommensteuer, "soli": -regel_soli, "kirchensteuer": -regel_kirchensteuer, "gesamt_steuer": -regel_gesamt_steuer, "netto": regel_netto, "vorteil": Decimal('0'), "calc": regel_calc}
    }
