# gui.py
from decimal import Decimal
import matplotlib.pyplot as plt
from steuer_berechner import berechne_steuer

def generate_plot(jahr, splitting, kirche, abfindung, zvst_eink_start, progr_eink):
    # Generate data for the plot
    zvst_eink_values = [zvst_eink_start + i * 1000 for i in range(-20, 21)]
    netto_fuenftel_values = []
    netto_regel_values = []

    for zvst_eink in zvst_eink_values:
        if zvst_eink < 0:
            zvst_eink = Decimal(0)
        ergebnis_plot = berechne_steuer(
            jahr=jahr,
            splitting=splitting,
            kirche=kirche,
            abfindung=abfindung,
            zvst_eink=zvst_eink,
            progr_eink=progr_eink
        )
        netto_fuenftel_values.append(ergebnis_plot['fuenftel']['netto'])
        netto_regel_values.append(ergebnis_plot['regel']['netto'])

    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(zvst_eink_values, netto_fuenftel_values, marker='o', linestyle='-', label="Fünftel-Regelung")
    ax.plot(zvst_eink_values, netto_regel_values, marker='o', linestyle='-', label="Regelbesteuerung")
    ax.set_xlabel("Zu versteuerndes Einkommen (€)")
    ax.set_ylabel("Netto nach Steuern (€)")
    ax.set_title("Netto nach Steuern vs. Zvst. Einkommen")
    ax.legend()
    ax.grid(True)
    fig.savefig("plot.png")

if __name__ == "__main__":
    # Default values for testing
    generate_plot(
        jahr=2025,
        splitting=False,
        kirche=False,
        abfindung=Decimal("100000"),
        zvst_eink_start=Decimal("50000"),
        progr_eink=Decimal("0")
    )
