import tkinter as tk
from tkinter import ttk
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from steuer_berechner import berechne_steuer


def generate_plot(jahr, splitting, kirche, abfindung, zvst_eink_start, progr_eink):
    # Generate data for the plot
    zvst_eink_values = [zvst_eink_start + i * 1000 for i in range(-50, 51)]
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

    return fig


def show_plot():
    # Get the input values from the GUI fields
    jahr = int(entry_jahr.get())
    splitting = var_splitting.get() == 1
    kirche = var_kirche.get() == 1
    abfindung = Decimal(entry_abfindung.get())
    zvst_eink_start = Decimal(entry_zvst_eink.get())
    progr_eink = Decimal(entry_progr_eink.get())

    # Generate the plot based on the user input
    fig = generate_plot(jahr, splitting, kirche, abfindung, zvst_eink_start, progr_eink)

    # Clear previous canvas if there is one
    for widget in frame_plot.winfo_children():
        widget.destroy()

    # Create a new canvas to display the plot
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack()


# Set up the main window
root = tk.Tk()
root.title("Steuerberechnung Plot")

# Set up the input fields
frame_inputs = ttk.LabelFrame(root, text="Eingabewerte", padding="10")
frame_inputs.grid(row=0, column=0, padx=10, pady=10)

# Jahr
ttk.Label(frame_inputs, text="Jahr:").grid(row=0, column=0, sticky="w")
entry_jahr = ttk.Entry(frame_inputs)
entry_jahr.grid(row=0, column=1)
entry_jahr.insert(0, "2025")

# Splitting
ttk.Label(frame_inputs, text="Ehegatten-Splitting:").grid(row=1, column=0, sticky="w")
var_splitting = tk.IntVar()
chk_splitting = ttk.Checkbutton(frame_inputs, variable=var_splitting)
chk_splitting.grid(row=1, column=1)

# Kirche
ttk.Label(frame_inputs, text="Kirchensteuerpflichtig:").grid(row=2, column=0, sticky="w")
var_kirche = tk.IntVar()
chk_kirche = ttk.Checkbutton(frame_inputs, variable=var_kirche)
chk_kirche.grid(row=2, column=1)

# Abfindung
ttk.Label(frame_inputs, text="Abfindung (€):").grid(row=3, column=0, sticky="w")
entry_abfindung = ttk.Entry(frame_inputs)
entry_abfindung.grid(row=3, column=1)
entry_abfindung.insert(0, "200000")

# Zu versteuerndes Einkommen
ttk.Label(frame_inputs, text="Zu versteuerndes Einkommen (€):").grid(row=4, column=0, sticky="w")
entry_zvst_eink = ttk.Entry(frame_inputs)
entry_zvst_eink.grid(row=4, column=1)
entry_zvst_eink.insert(0, "50000")

# Progressionsvorbehalt
ttk.Label(frame_inputs, text="Progressionsvorbehalt (€):").grid(row=5, column=0, sticky="w")
entry_progr_eink = ttk.Entry(frame_inputs)
entry_progr_eink.grid(row=5, column=1)
entry_progr_eink.insert(0, "0")

# Submit button
btn_plot = ttk.Button(frame_inputs, text="Plot generieren", command=show_plot)
btn_plot.grid(row=6, column=0, columnspan=2, pady=10)

# Frame for the plot
frame_plot = ttk.Frame(root, width=800, height=600)
frame_plot.grid(row=1, column=0, padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
