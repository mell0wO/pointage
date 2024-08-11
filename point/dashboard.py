import sys
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton, QHBoxLayout
from sqlalchemy import create_engine
from matplotlib.dates import DateFormatter

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jour de la Semaine vs Travail")
        self.setGeometry(100, 100, 1200, 800)

        # Create a widget for the central area
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create the main layout
        self.layout = QVBoxLayout(self.central_widget)

        # Create a filter layout for month and name selection
        self.filter_layout = QHBoxLayout()
        self.layout.addLayout(self.filter_layout)

        # Month selection dropdown
        self.month_combobox = QComboBox()
        self.month_combobox.addItem("Tous les mois")
        for month in range(1, 13):
            self.month_combobox.addItem(f"{month:02d}")

        self.filter_layout.addWidget(self.month_combobox)

        # Name selection dropdown
        self.name_combobox = QComboBox()
        self.name_combobox.addItem("Tous les noms")  # Placeholder item
        self.filter_layout.addWidget(self.name_combobox)

        # Apply filter button
        self.apply_button = QPushButton("Appliquer le Filtre")
        self.apply_button.clicked.connect(self.apply_filter)
        self.filter_layout.addWidget(self.apply_button)

        # Create the matplotlib figure and axes
        self.figure, self.ax = plt.subplots(3, 2, figsize=(12, 18))  # Trois lignes, deux colonnes

        # Create the canvas and add it to the layout
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)

        # Load and process data
        self.load_and_process_data()

        # Initialize filtered_df to the full dataset
        self.filtered_df = self.df

        # Plot the data
        self.plot_data()

    def load_and_process_data(self):
        try:
            # Create a database engine
            engine = create_engine('postgresql://postgres:mellowo@localhost:5432/bi')

            # Read data from the database into a DataFrame
            self.df = pd.read_sql('SELECT * FROM dbbi', engine)

            # Print column names and a few rows for verification
            print("Column names:", self.df.columns)
            print("Sample data:\n", self.df.head())

            # Populate the name combobox with values from 'nom'
            if 'nom' in self.df.columns:
                noms = self.df['nom'].dropna().unique()  # Drop NaN values and get unique names
                cleaned_noms = [nom.strip() for nom in noms]  # Remove any leading/trailing spaces
                unique_noms = sorted(set(cleaned_noms))  # Remove duplicates and sort
                self.name_combobox.clear()  # Clear existing items
                self.name_combobox.addItems(["Tous les noms"] + unique_noms)  # Add items to combobox
            else:
                print("Column 'nom' does not exist in the DataFrame.")

            # Ensure the 'date' column is in datetime format
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

                # Function to get day of the week from a datetime object
                def get_day_of_week(date_obj):
                    return date_obj.strftime("%A") if pd.notna(date_obj) else None

                # Apply the function to the 'date' column and create a new column 'Jour_de_la_Semaine'
                self.df['Jour_de_la_Semaine'] = self.df['date'].apply(get_day_of_week)

                # Convert 'travail' to a numeric format for plotting
                self.df['travail'] = pd.to_timedelta(self.df['travail']).dt.total_seconds() / 3600  # Convertir en heures
            else:
                print("Column 'date' does not exist in the DataFrame.")

        except Exception as e:
            print(f"Erreur lors du chargement et du traitement des données : {e}")
            self.df = pd.DataFrame()  # Définir sur DataFrame vide en cas d'erreur

    def apply_filter(self):
        try:
            # Get the selected month and name from the comboboxes
            selected_month = self.month_combobox.currentText()
            selected_name = self.name_combobox.currentText()

            # Convert selected_month to integer if it's not "Tous les mois"
            if selected_month != "Tous les mois":
                selected_month = int(selected_month)
            else:
                selected_month = None

            # Filter by month
            if 'date' in self.df.columns:
                if selected_month is not None:
                    # Filter by month
                    month_filtered_df = self.df[self.df['date'].dt.month == selected_month]
                else:
                    month_filtered_df = self.df

                # Filter by name
                if selected_name != "Tous les noms":
                    self.filtered_df = month_filtered_df[month_filtered_df['nom'] == selected_name]
                else:
                    self.filtered_df = month_filtered_df

                # Print filtered DataFrame for debugging
                print("Filtered DataFrame:\n", self.filtered_df)
            else:
                print("Column 'date' does not exist in the DataFrame.")
                self.filtered_df = pd.DataFrame()  # Set to empty DataFrame if date column is missing

            # Re-plot the data with the selected filters
            self.plot_data()

        except Exception as e:
            print(f"Erreur lors de l'application du filtre : {e}")
            self.filtered_df = pd.DataFrame()  # Set to empty DataFrame in case of error

    def plot_data(self):
        if self.filtered_df.empty:
            # Clear previous charts
            for ax in self.ax.flatten():
                ax.clear()

            # Display a message on the charts indicating no data
            for ax in self.ax.flatten():
                ax.text(0.5, 0.5, 'Aucune donnée disponible pour le graphique', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12, color='red')

            self.canvas.draw()
            return

        # Filter out Saturday and Sunday for the bar chart
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        weekdays_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']  # Days in French

        # Filter data for the selected month
        filtered_df = self.filtered_df[self.filtered_df['Jour_de_la_Semaine'].isin(weekdays)]

        # Group by 'Jour_de_la_Semaine' and sum the 'travail'
        grouped = filtered_df.groupby('Jour_de_la_Semaine')['travail'].sum().reindex(weekdays, fill_value=0)
        grouped.index = weekdays_fr  # Rename days to French

        self.ax[0, 0].clear()
        bars = self.ax[0, 0].bar(grouped.index, grouped.values, color='skyblue')

        # Highlight highest and lowest values
        highest_day = grouped.idxmax()
        lowest_day = grouped.idxmin()
        self.ax[0, 0].bar(highest_day, grouped.max(), color='green', edgecolor='black')
        self.ax[0, 0].bar(lowest_day, grouped.min(), color='red', edgecolor='black')

        self.ax[0, 0].set_xlabel('Jour de la Semaine')
        self.ax[0, 0].set_ylabel('Total Travail (heures)')
        self.ax[0, 0].set_title('Total Travail par Jour de la Semaine')

        # Add interactive tooltips for the bar chart only
        mplcursors.cursor(bars, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f'{grouped.index[sel.index]}: {grouped.values[sel.index]:.1f} heures')
        )

        # Plot the travail for each date, including missing dates
        all_dates = pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max())
        full_df = pd.DataFrame({'date': all_dates})
        full_df = full_df.merge(self.filtered_df[['date', 'travail']], on='date', how='left').fillna({'travail': 0})

        self.ax[0, 1].clear()
        line = self.ax[0, 1].plot(full_df['date'], full_df['travail'], marker='o', color='blue')[0]

        # Highlight the highest and lowest values in the line chart
        max_value = full_df['travail'].max()
        min_value = full_df['travail'].min()
        max_date = full_df.loc[full_df['travail'] == max_value, 'date'].iloc[0]
        min_date = full_df.loc[full_df['travail'] == min_value, 'date'].iloc[0]
        self.ax[0, 1].plot(max_date, max_value, 'go', markersize=10)  # Green point for max
        self.ax[0, 1].plot(min_date, min_value, 'ro', markersize=10)  # Red point for min

        # Change line color to indicate threshold
        self.ax[0, 1].plot(full_df['date'], full_df['travail'], color='blue')
        self.ax[0, 1].axhline(y=8, color='red', linestyle='--', label='Seuil de 8 heures')

        self.ax[0, 1].set_xlabel('Date')
        self.ax[0, 1].set_ylabel('Travail (heures)')
        self.ax[0, 1].set_title('Travail au Fil du Temps')
        self.ax[0, 1].xaxis.set_major_formatter(DateFormatter('%d-%m-%Y'))

        # Add interactive tooltips for the line chart (if needed, otherwise remove this section)
        # mplcursors.cursor(line, hover=True).connect(
        #     "add", lambda sel: sel.annotation.set_text(f'{full_df["date"].iloc[sel.index].strftime("%d-%m-%Y")}: {full_df["travail"].iloc[sel.index]:.1f} heures')
        # )

        # Plot the total travail per month
        monthly_totals = self.filtered_df.groupby(self.filtered_df['date'].dt.to_period('M')).agg({'travail': 'sum'})
        monthly_totals.index = monthly_totals.index.to_timestamp()

        self.ax[1, 0].clear()
        bars = self.ax[1, 0].bar(monthly_totals.index.strftime('%Y-%m'), monthly_totals['travail'], color='skyblue')

        self.ax[1, 0].set_xlabel('Mois')
        self.ax[1, 0].set_ylabel('Total Travail (heures)')
        self.ax[1, 0].set_title('Total Travail par Mois')

        # Add interactive tooltips for the bar chart only
        mplcursors.cursor(bars, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f'{monthly_totals.index[sel.index].strftime("%Y-%m")}: {monthly_totals["travail"].iloc[sel.index]:.1f} heures')
        )

        # Plot the number of days of travail per month
        days_of_travail = monthly_totals['travail'] / 8  # Convert hours to days

        self.ax[1, 1].clear()
        line = self.ax[1, 1].plot(days_of_travail.index, days_of_travail, marker='o', color='blue')[0]

        self.ax[1, 1].set_xlabel('Mois')
        self.ax[1, 1].set_ylabel('Nombre de Jours de Travail')
        self.ax[1, 1].set_title('Nombre de Jours de Travail par Mois')

        # Add interactive tooltips for the line chart (if needed, otherwise remove this section)
        # mplcursors.cursor(line, hover=True).connect(
        #     "add", lambda sel: sel.annotation.set_text(f'{days_of_travail.index[sel.index].strftime("%Y-%m")}: {days_of_travail.iloc[sel.index]:.1f} jours')
        # )

        # Doughnut chart showing the number of travail hours vs. expected hours
        expected_hours_per_week = 40
        actual_hours = self.filtered_df['travail'].sum()
        total_weeks = len(pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max(), freq='W'))

        expected_hours = expected_hours_per_week * total_weeks

        # Ensure non-negative values
        actual_hours = max(0, actual_hours)
        expected_hours = max(0, expected_hours)

        self.ax[2, 0].clear()
        if expected_hours > 0:  # Check if there's a positive expected_hours value
            self.ax[2, 0].pie(
                [actual_hours, expected_hours - actual_hours],
                labels=['Heures Réelles', 'Heures Attendues'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#ff9999', '#66b3ff'],
                wedgeprops=dict(width=0.3)  # Makes the pie chart into a doughnut chart
            )
            self.ax[2, 0].set_title('Heures Réelles vs Heures Attendues')
        else:
            self.ax[2, 0].text(0.5, 0.5, 'Pas d\'heures attendues à afficher',
                                horizontalalignment='center', verticalalignment='center',
                                transform=self.ax[2, 0].transAxes, fontsize=12, color='red')

        # New: Find the most and least worked employees
        if 'nom' in self.filtered_df.columns:
            employee_totals = self.filtered_df.groupby('nom')['travail'].sum()
            most_worked_employee = employee_totals.idxmax()
            least_worked_employee = employee_totals.idxmin()

            self.ax[2, 1].clear()
            self.ax[2, 1].text(0.5, 0.6, f"Employé le Plus Travaillé: {most_worked_employee}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax[2, 1].transAxes, fontsize=12, color='green')
            self.ax[2, 1].text(0.5, 0.4, f"Employé le Moins Travaillé: {least_worked_employee}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax[2, 1].transAxes, fontsize=12, color='red')
            self.ax[2, 1].set_title('Employés Travaillés')

        self.ax[2, 1].axis('off')
        plt.subplots_adjust(wspace=0.5, hspace=0.5)  
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())
