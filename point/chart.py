import sys
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine
from matplotlib.dates import DateFormatter

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create horizontal splitter
        horizontal_splitter = QSplitter(Qt.Horizontal)

        # Create top and bottom widgets for the horizontal splitter
        top_widget = QWidget()
        bottom_widget = QWidget()
        
        horizontal_splitter.addWidget(top_widget)
        horizontal_splitter.addWidget(bottom_widget)
        
        # Create vertical splitters for top and bottom sections
        top_splitter = QSplitter(Qt.Vertical)
        bottom_splitter = QSplitter(Qt.Vertical)
        
        top_widget.setLayout(QVBoxLayout())
        top_widget.layout().addWidget(top_splitter)
        
        bottom_widget.setLayout(QVBoxLayout())
        bottom_widget.layout().addWidget(bottom_splitter)
        
        # Create the sections in the top splitter
        self.barjr = QFrame()
        self.barmoi = QFrame()
        self.mm = QFrame()
        
        top_splitter.addWidget(self.barjr)
        top_splitter.addWidget(self.barmoi)
        top_splitter.addWidget(self.mm)
        
        # Create the sections in the bottom splitter
        self.linjr = QFrame()
        self.linmoi = QFrame()
        self.daugh = QFrame()
        
        bottom_splitter.addWidget(self.linjr)
        bottom_splitter.addWidget(self.linmoi)
        bottom_splitter.addWidget(self.daugh)
        
        # Set sizes for the sections in the splitters
        top_splitter.setSizes([150, 150, 200])  # Adjust sizes as needed
        bottom_splitter.setSizes([150, 150, 200])  # Adjust sizes as needed
        
        # Add horizontal splitter to the main layout
        main_layout.addWidget(horizontal_splitter)

        self.setWindowTitle("Split Layout Example")
        self.resize(800, 600)  # Set initial size of the window
        
        # Create and add matplotlib figures to the frames
        self.init_matplotlib()

    def init_matplotlib(self):
        # Create matplotlib figures for each section
        self.figures = {
            "barjr": plt.Figure(figsize=(6, 4)),
            "barmoi": plt.Figure(figsize=(6, 4)),
            "mm": plt.Figure(figsize=(6, 4)),
            "linjr": plt.Figure(figsize=(6, 4)),
            "linmoi": plt.Figure(figsize=(6, 4)),
            "daugh": plt.Figure(figsize=(6, 4))
        }
        
        self.canvases = {}
        self.axs = {}

        for key, fig in self.figures.items():
            self.canvases[key] = FigureCanvas(fig)
            self.axs[key] = fig.add_subplot(111)
            if key == "barjr":
                self.barjr_layout = QVBoxLayout(self.barjr)
                self.barjr_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.barjr_layout.addWidget(self.canvases[key])
            elif key == "barmoi":
                self.barmoi_layout = QVBoxLayout(self.barmoi)
                self.barmoi_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.barmoi_layout.addWidget(self.canvases[key])
            elif key == "mm":
                self.mm_layout = QVBoxLayout(self.mm)
                self.mm_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.mm_layout.addWidget(self.canvases[key])
            elif key == "linjr":
                self.linjr_layout = QVBoxLayout(self.linjr)
                self.linjr_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.linjr_layout.addWidget(self.canvases[key])
            elif key == "linmoi":
                self.linmoi_layout = QVBoxLayout(self.linmoi)
                self.linmoi_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.linmoi_layout.addWidget(self.canvases[key])
            elif key == "daugh":
                self.daugh_layout = QVBoxLayout(self.daugh)
                self.daugh_layout.addWidget(NavigationToolbar(self.canvases[key], self))
                self.daugh_layout.addWidget(self.canvases[key])

    def plot_data(self):
        if hasattr(self, 'filtered_df') and not self.filtered_df.empty:
            # Bar chart for 'Jour_de_la_Semaine'
            self.plot_bar_jr()

            # Bar chart for 'Total Travail par Mois'
            self.plot_bar_moi()

            # Best and Worst Names
            self.plot_mm()

            # Line chart for 'Travail au Fil du Temps'
            self.plot_lin_jr()

            # Line chart for 'Nombre de Jours de Travail par Mois'
            self.plot_lin_moi()

            # Doughnut chart for 'Heures Réelles vs Heures Attendues'
            self.plot_daugh()

    def plot_bar_jr(self):
        # Example plotting code for barjr
        if 'Jour_de_la_Semaine' in self.filtered_df.columns:
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            weekdays_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']

            filtered_df = self.filtered_df[self.filtered_df['Jour_de_la_Semaine'].isin(weekdays)]
            grouped = filtered_df.groupby('Jour_de_la_Semaine')['travail'].sum().reindex(weekdays, fill_value=0)
            grouped.index = weekdays_fr

            self.axs["barjr"].clear()
            bars = self.axs["barjr"].bar(grouped.index, grouped.values, color='skyblue')

            # Highlight highest and lowest values
            highest_day = grouped.idxmax()
            lowest_day = grouped.idxmin()
            self.axs["barjr"].bar(highest_day, grouped.max(), color='green', edgecolor='black')
            self.axs["barjr"].bar(lowest_day, grouped.min(), color='red', edgecolor='black')

            self.axs["barjr"].set_xlabel('Jour de la Semaine')
            self.axs["barjr"].set_ylabel('Total Travail (heures)')
            self.axs["barjr"].set_title('Total Travail par Jour de la Semaine')
            mplcursors.cursor(bars, hover=True).connect(
                "add", lambda sel: sel.annotation.set_text(f'{grouped.index[sel.index]}: {grouped.values[sel.index]:.1f} heures')
            )

            self.canvases["barjr"].draw()

    def plot_bar_moi(self):
        # Example plotting code for barmoi
        if 'date' in self.filtered_df.columns:
            monthly_totals = self.filtered_df.groupby(self.filtered_df['date'].dt.to_period('M')).agg({'travail': 'sum'})
            monthly_totals.index = monthly_totals.index.to_timestamp()

            self.axs["barmoi"].clear()
            bars = self.axs["barmoi"].bar(monthly_totals.index.strftime('%Y-%m'), monthly_totals['travail'], color='skyblue')

            self.axs["barmoi"].set_xlabel('Mois')
            self.axs["barmoi"].set_ylabel('Total Travail (heures)')
            self.axs["barmoi"].set_title('Total Travail par Mois')
            mplcursors.cursor(bars, hover=True).connect(
                "add", lambda sel: sel.annotation.set_text(f'{monthly_totals.index[sel.index].strftime("%Y-%m")}: {monthly_totals["travail"].iloc[sel.index]:.1f} heures')
            )

            self.canvases["barmoi"].draw()

    def plot_mm(self):
        # Example plotting code for mm
        if 'nom' in self.filtered_df.columns:
            employee_totals = self.filtered_df.groupby('nom')['travail'].sum()
            most_worked_employee = employee_totals.idxmax()
            least_worked_employee = employee_totals.idxmin()

            self.axs["mm"].clear()
            self.axs["mm"].text(0.5, 0.6, f"Employé le Plus Travaillé: {most_worked_employee}",
                                horizontalalignment='center', verticalalignment='center',
                                transform=self.axs["mm"].transAxes, fontsize=12, color='green')
            self.axs["mm"].text(0.5, 0.4, f"Employé le Moins Travaillé: {least_worked_employee}",
                                horizontalalignment='center', verticalalignment='center',
                                transform=self.axs["mm"].transAxes, fontsize=12, color='red')
            self.axs["mm"].set_title('Meilleurs et Moins Bons Employés')
            self.axs["mm"].axis('off')

            self.canvases["mm"].draw()

    def plot_lin_jr(self):
        # Example plotting code for linjr
        if 'date' in self.filtered_df.columns:
            daily_totals = self.filtered_df.groupby(self.filtered_df['date']).agg({'travail': 'sum'})

            self.axs["linjr"].clear()
            self.axs["linjr"].plot(daily_totals.index, daily_totals['travail'], marker='o', linestyle='-')

            self.axs["linjr"].set_xlabel('Date')
            self.axs["linjr"].set_ylabel('Travail (heures)')
            self.axs["linjr"].set_title('Évolution du Travail au Fil du Temps')

            # Format x-axis to show only dates with work
            self.axs["linjr"].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

            self.canvases["linjr"].draw()

    def plot_lin_moi(self):
        # Example plotting code for linmoi
        if 'date' in self.filtered_df.columns:
            monthly_days_worked = self.filtered_df.groupby(self.filtered_df['date'].dt.to_period('M')).size()

            self.axs["linmoi"].clear()
            self.axs["linmoi"].plot(monthly_days_worked.index.to_timestamp(), monthly_days_worked.values, marker='o', linestyle='-')

            self.axs["linmoi"].set_xlabel('Mois')
            self.axs["linmoi"].set_ylabel('Nombre de Jours de Travail')
            self.axs["linmoi"].set_title('Nombre de Jours de Travail par Mois')

            # Format x-axis to show months
            self.axs["linmoi"].xaxis.set_major_formatter(DateFormatter('%Y-%m'))

            self.canvases["linmoi"].draw()

    def plot_daugh(self):
        # Example plotting code for daugh
        if hasattr(self, 'expected_hours') and 'travail' in self.filtered_df.columns:
            total_worked_hours = self.filtered_df['travail'].sum()
            expected_hours = self.expected_hours

            labels = ['Heures Travaillées', 'Heures Attendues']
            sizes = [total_worked_hours, expected_hours - total_worked_hours]
            colors = ['#ff9999','#66b3ff']
            explode = (0.1, 0)  # explode 1st slice

            self.axs["daugh"].clear()
            self.axs["daugh"].pie(sizes, explode=explode, labels=labels, colors=colors,
                                 autopct='%1.1f%%', shadow=True, startangle=140)
            self.axs["daugh"].set_title('Comparaison des Heures Travaillées et Attendues')

            self.canvases["daugh"].draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
