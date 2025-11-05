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
    Dies ist eine interne Hilfsfunktion.
    """
    zve = Decimal(zu_versteuerndes_einkommen)

    # Splitting-Verfahren
    if splitting:
        zve /= 2

    gfb = Decimal('12096') # Grundfreibetrag 2025 (Annahme)

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

def _berechne_soli(einkommensteuer, splitting):
    """
    Berechnet den Solidaritätszuschlag unter Berücksichtigung der Freigrenze und Milderungszone.
    """
    freigrenze = Decimal('39900') if splitting else Decimal('19950')

    if einkommensteuer <= freigrenze:
        return Decimal('0')

    # Milderungszone
    # Der Soli darf 11,9 % des Unterschiedsbetrags zwischen Lohnsteuer und Freigrenze nicht übersteigen.
    soli_milderung = (einkommensteuer - freigrenze) * Decimal('0.119')

    # Voller Soli
    soli_voll = einkommensteuer * SOLIDARITATSZUSCHLAG_SATZ

    # Der niedrigere der beiden Werte ist der anzusetzende Soli
    return min(soli_milderung, soli_voll).quantize(Decimal('0.01'))


def berechne_steuer(jahr, splitting, kirche, abfindung, zvst_eink, progr_eink):
    """
    Berechnet die Steuerlast sowohl nach der Regelbesteuerung als auch nach der Fünftelregelung.
    """
    abfindung = Decimal(abfindung)
    zvst_eink = Decimal(zvst_eink)
    progr_eink = Decimal(progr_eink)

    # --- Regelbesteuerung ---
    regel_gesamteinkuenfte = zvst_eink + abfindung
    regel_gesamteinkuenfte_prog = regel_gesamteinkuenfte + progr_eink

    regel_einkommensteuer = _berechne_einkommensteuer_basis(regel_gesamteinkuenfte_prog, splitting)

    regel_soli = _berechne_soli(regel_einkommensteuer, splitting)

    regel_kirchensteuer = Decimal('0')
    if kirche:
        regel_kirchensteuer = (regel_einkommensteuer * KIRCHENSTEUER_SATZ).quantize(Decimal('0.01'))

    regel_gesamt_steuer = regel_einkommensteuer + regel_soli + regel_kirchensteuer
    regel_netto = regel_gesamteinkuenfte - regel_gesamt_steuer

    # --- Fünftel-Regelung ---
    fuenftel_gesamteinkuenfte = zvst_eink
    fuenftel_gesamteinkuenfte_prog = fuenftel_gesamteinkuenfte + progr_eink

    est_auf_zvst_eink = _berechne_einkommensteuer_basis(fuenftel_gesamteinkuenfte_prog, splitting)
    est_auf_zvst_eink_plus_fuenftel = _berechne_einkommensteuer_basis(fuenftel_gesamteinkuenfte_prog + (abfindung / 5), splitting)

    fuenftel_einkommensteuer_abfindung = (est_auf_zvst_eink_plus_fuenftel - est_auf_zvst_eink) * 5
    fuenftel_einkommensteuer_gesamt = est_auf_zvst_eink + fuenftel_einkommensteuer_abfindung

    fuenftel_soli = _berechne_soli(fuenftel_einkommensteuer_gesamt, splitting)

    fuenftel_kirchensteuer = Decimal('0')
    if kirche:
        fuenftel_kirchensteuer = (fuenftel_einkommensteuer_gesamt * KIRCHENSTEUER_SATZ).quantize(Decimal('0.01'))

    fuenftel_gesamt_steuer = fuenftel_einkommensteuer_gesamt + fuenftel_soli + fuenftel_kirchensteuer
    fuenftel_netto = fuenftel_gesamteinkuenfte + abfindung - fuenftel_gesamt_steuer

    vorteil_fuenftel = regel_gesamt_steuer - fuenftel_gesamt_steuer

    fuenftel_steuersatz_gesamt = (fuenftel_gesamt_steuer / (fuenftel_gesamteinkuenfte + abfindung) * 100) if (fuenftel_gesamteinkuenfte + abfindung) > 0 else Decimal('0')
    regel_steuersatz_gesamt = (regel_gesamt_steuer / regel_gesamteinkuenfte * 100) if regel_gesamteinkuenfte > 0 else Decimal('0')
    fuenftel_steuersatz_einkommen = (fuenftel_einkommensteuer_gesamt / (fuenftel_gesamteinkuenfte + abfindung) * 100) if (fuenftel_gesamteinkuenfte + abfindung) > 0 else Decimal('0')
    regel_steuersatz_einkommen = (regel_einkommensteuer / regel_gesamteinkuenfte * 100) if regel_gesamteinkuenfte > 0 else Decimal('0')


    return {
        "fuenftel": {
            "einkommensteuer": -fuenftel_einkommensteuer_gesamt, "soli": -fuenftel_soli, "kirchensteuer": -fuenftel_kirchensteuer,
            "gesamt_steuer": -fuenftel_gesamt_steuer, "netto": fuenftel_netto, "vorteil": vorteil_fuenftel,
            "calc": {
                "gesamteinkuenfte": fuenftel_gesamteinkuenfte, "gesamteinkuenfte_prog": fuenftel_gesamteinkuenfte_prog,
                "einkommensteuersatz_gesamt": fuenftel_steuersatz_einkommen, "weitere_einkuenfte": Decimal('0'),
                "weitere_einkuenfte_prog": Decimal('0'), "einkommensteuersatz_sonstige": Decimal('0'),
                "einkommensteuer_sonstige": Decimal('0'), "einkommensteuer_fuenftel_regelung": -fuenftel_einkommensteuer_abfindung,
                "einkommensteuer_gesamt": -fuenftel_einkommensteuer_gesamt, "soli": -fuenftel_soli,
                "kirchensteuer": -fuenftel_kirchensteuer, "steuer_gesamt": -fuenftel_gesamt_steuer,
                "einkommensteuersatz_einmalzahlung": fuenftel_steuersatz_einkommen,
                "einkommensteuersatz_gesamt_unten": fuenftel_steuersatz_gesamt
            }
        },
        "regel": {
            "einkommensteuer": -regel_einkommensteuer, "soli": -regel_soli, "kirchensteuer": -regel_kirchensteuer,
            "gesamt_steuer": -regel_gesamt_steuer, "netto": regel_netto, "vorteil": Decimal('0'),
            "calc": {
                "gesamteinkuenfte": regel_gesamteinkuenfte, "gesamteinkuenfte_prog": regel_gesamteinkuenfte_prog,
                "einkommensteuersatz_gesamt": regel_steuersatz_einkommen, "weitere_einkuenfte": Decimal('0'),
                "weitere_einkuenfte_prog": Decimal('0'), "einkommensteuersatz_sonstige": Decimal('0'),
                "einkommensteuer_sonstige": Decimal('0'), "einkommensteuer_fuenftel_regelung": Decimal('0'),
                "einkommensteuer_gesamt": -regel_einkommensteuer, "soli": -regel_soli,
                "kirchensteuer": -regel_kirchensteuer, "steuer_gesamt": -regel_gesamt_steuer,
                "einkommensteuersatz_einmalzahlung": Decimal('0'),
                "einkommensteuersatz_gesamt_unten": regel_steuersatz_gesamt
            }
        }
    }
