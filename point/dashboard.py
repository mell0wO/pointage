import sys
from matplotlib.table import Table
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem
from sqlalchemy import create_engine
from matplotlib.dates import DateFormatter
import seaborn as sns

class Dashboard(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jour de la Semaine vs Travail")
        self.setGeometry(100, 100, 1200, 800)
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()

        self.filter_layout = QHBoxLayout()
        self.layout.addLayout(self.filter_layout)

        self.month_listwidget = QListWidget()
        self.month_listwidget.addItem("Tous les mois")
        for month in range(1, 13):
            self.month_listwidget.addItem(f"{month:02d}")
        self.month_listwidget.setSelectionMode(QListWidget.MultiSelection)
        self.filter_layout.addWidget(self.month_listwidget)

        self.name_listwidget = QListWidget()
        self.name_listwidget.addItem("Tous les noms")
        self.name_listwidget.setSelectionMode(QListWidget.MultiSelection)
        self.filter_layout.addWidget(self.name_listwidget)

        self.apply_button = QPushButton("Appliquer le Filtre")
        self.apply_button.clicked.connect(self.apply_filter)
        self.filter_layout.addWidget(self.apply_button)
        self.apply_button.setStyleSheet("""
            QPushButton {
            background-color: #1887f5;
            color: white;
            border: none;
            padding: 10px;
            }
            QPushButton:hover {
                background-color: #0578eb;
                }
        """)

        self.figure, self.ax = plt.subplots(3, 2, figsize=(12, 18))

        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)

        self.load_and_process_data()
        self.filtered_df = self.df
        self.plot_data()

    def load_and_process_data(self):
        try:
            # créer un moteur de base de données
            engine = create_engine('postgresql://postgres:mellowo@localhost:5432/bi')

            # lire les données de la base de données dans un DataFrame
            self.df = pd.read_sql('SELECT * FROM dbbi', engine)

            # afficher les noms des colonnes et quelques lignes pour vérification
            print("Column names:", self.df.columns)
            print("Sample data:\n", self.df.head())

            if 'nom' in self.df.columns:
                noms = self.df['nom'].dropna().unique()  # supprimer les valeurs NaN et obtenir les noms uniques
                cleaned_noms = [nom.strip() for nom in noms] # supprimer les espaces au début/à la fin
                unique_noms = sorted(set(cleaned_noms)) # supprimer les doublons et trier
                self.name_listwidget.clear()  # vider les éléments existants
                self.name_listwidget.addItems(["Tous les noms"] + unique_noms)
            else:
                print("Column 'nom' does not exist in the DataFrame.")

            # s'assurer que la colonne 'date' est au format datetime
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
                self.df['month'] = self.df['date'].dt.month

            # fonction pour obtenir le jour de la semaine à partir d'un objet datetime
                def get_day_of_week(date_obj):
                    return date_obj.strftime("%A") if pd.notna(date_obj) else None

                # appliquer la fonction à la colonne 'date' et créer une nouvelle colonne 'Jour_de_la_Semaine'
                self.df['Jour_de_la_Semaine'] = self.df['date'].apply(get_day_of_week)

                # convertir 'travail' en format numérique pour l'affichage
                self.df['travail'] = pd.to_timedelta(self.df['travail']).dt.total_seconds() / 3600  # convertir en heures
            else:
                print("Column 'date' does not exist in the DataFrame.")

        except Exception as e:
            print(f"Erreur lors du chargement et du traitement des données : {e}")
            self.df = pd.DataFrame()  # définir sur DataFrame vide en cas d'erreur

    def apply_filter(self):
        try:
            print("Initial DataFrame:\n", self.df.head())

            selected_months = []
            selected_items = self.month_listwidget.selectedItems()

            # vérifier si 'tous les mois' est sélectionné
            if any(item.text() == 'tous les mois' for item in selected_items):
                selected_months.append('tous les mois')
            else:
                # convertir les valeurs numériques des mois
                selected_months = [int(item.text()) for item in selected_items if item.text().isdigit()]
            selected_names = [item.text() for item in self.name_listwidget.selectedItems()]

            print("Selected months:", selected_months)
            print("Selected names:", selected_names)


            print("Selected months:", selected_months)
            print("Selected names:", selected_names)

            if 'date' in self.df.columns:
                # filtrer par mois sélectionné
                if selected_months:
                    month_filtered_df = self.df[self.df['date'].dt.month.isin(selected_months)]
                else:
                    month_filtered_df = self.df

                # filtrer par nom sélectionné

                if "Tous les noms" not in selected_names:
                    self.filtered_df = month_filtered_df[month_filtered_df['nom'].isin(selected_names)]
                else:
                    self.filtered_df = month_filtered_df

                # effacer les éléments actuels de QListWidget
                self.list_widget.clear()

                # remplir le QListWidget avec les données filtrées
                for _, row in self.filtered_df.iterrows():
                    item_text = f"{row['nom']} - {row['date']}"  # Customize this to display what you want
                    list_item = QListWidgetItem(item_text)
                    self.list_widget.addItem(list_item)

                self.list_widget.clear()

                # remplir le QListWidget avec les données filtrées
                for _, row in self.filtered_df.iterrows():
                    item_text = f"{row['nom']} - {row['date']}"  # Customize this to display what you want
                    list_item = QListWidgetItem(item_text)
                    self.list_widget.addItem(list_item)

                print("Filtered DataFrame:\n", self.filtered_df)

            else:
                print("Column 'date' does not exist in the DataFrame.")
                self.filtered_df = pd.DataFrame()

            self.plot_data()

        except Exception as e:
            print(f"Erreur lors de l'application du filtre : {e}")
            self.filtered_df = pd.DataFrame() 

    def plot_data(self):

        if self.filtered_df.empty:
            # effacer les graphiques précédents
            for ax in self.ax.flatten():
                ax.clear()

            # afficher un message sur les graphiques indiquant qu'il n'y a pas de données
            for ax in self.ax.flatten():
                ax.text(0.5, 0.5, 'Aucune donnée disponible pour le graphique', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12, color='red')

            self.canvas.draw()
            return

        # exclure le samedi et le dimanche pour le graphique en barres
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        weekdays_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
        # filtrer les données pour le mois sélectionné
        filtered_df = self.filtered_df[self.filtered_df['Jour_de_la_Semaine'].isin(weekdays)]

        # grouper par 'Jour_de_la_Semaine' et calculer la moyenne du 'travail'
        grouped = filtered_df.groupby('Jour_de_la_Semaine')['travail'].mean().reindex(weekdays, fill_value=0)
        grouped.index = weekdays_fr 

        self.ax[1, 0].clear()
        sns.barplot(x=grouped.index, y=grouped.values, palette='Blues_d', ax=self.ax[1, 0])

        # vérifier si `grouped` contient des données avant de surligner les barres
        if len(grouped) > 0:
            # s'assurer que les indices sont dans la plage
            highest_day = grouped.idxmax()
            lowest_day = grouped.idxmin()
            try:
                highest_idx = grouped.index.get_loc(highest_day)
                lowest_idx = grouped.index.get_loc(lowest_day)
                self.ax[1, 0].patches[highest_idx].set_facecolor('green')
                self.ax[1, 0].patches[lowest_idx].set_facecolor('red')
            except IndexError:
                pass  # gérer le cas où les indices sont hors de la plage

        self.ax[1, 0].set_xlabel('Jour de la Semaine')
        self.ax[1, 0].set_ylabel('Moyenne Travail (heures)')
        self.ax[1, 0].set_title('Moyenne Travail par Jour de la Semaine')

        # s'assurer que la liste `patches` est remplie avant d'ajouter des infobulles interactives
        if hasattr(self.ax[1, 0], 'patches') and len(self.ax[1, 0].patches) > 0:
            mplcursors.cursor(self.ax[1, 0].patches, hover=True).connect(
                "add", lambda sel: sel.annotation.set_text(f'{grouped.index[sel.index]}: {grouped.values[sel.index]:.1f} heures')
            )

        # tracer le travail pour chaque date, y compris les dates manquantes
        all_dates = pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max())
        full_df = pd.DataFrame({'date': all_dates})
        full_df = full_df.merge(self.filtered_df[['date', 'travail']], on='date', how='left').fillna({'travail': 0})

        self.ax[1, 1].clear()
        sns.lineplot(x='date', y='travail', data=full_df, marker='o', color='blue', ax=self.ax[1, 1])

        # vérifier si `full_df` contient des données avant de tracer les points dans le graphique en ligne
        if not full_df.empty:
            avg_value = full_df['travail'].mean()
            max_date = full_df.loc[full_df['travail'] == full_df['travail'].max(), 'date'].iloc[0]
            min_date = full_df.loc[full_df['travail'] == full_df['travail'].min(), 'date'].iloc[0]
            self.ax[1, 1].plot(max_date, full_df['travail'].max(), 'go', markersize=10)
            self.ax[1, 1].plot(min_date, full_df['travail'].min(), 'ro', markersize=10)

        # changer la couleur de la ligne pour indiquer le seuil
        self.ax[1, 1].plot(full_df['date'], full_df['travail'], color='blue')
        self.ax[1, 1].axhline(y=8, color='red', linestyle='--', label='Seuil de 8 heures')
        self.ax[1, 1].axhline(y=avg_value, color='orange', linestyle='--', label='Moyenne Travail')

        self.ax[1, 1].set_xlabel('Date')
        self.ax[1, 1].set_ylabel('Travail (heures)')
        self.ax[1, 1].set_title('Travail au Fil du Temps')
        self.ax[1, 1].xaxis.set_major_formatter(DateFormatter('%d-%m-%Y'))

        # tracer le total du travail par mois
        monthly_totals = self.filtered_df.groupby(self.filtered_df['date'].dt.to_period('M')).agg({'travail': 'mean'})
        monthly_totals.index = monthly_totals.index.to_timestamp()

        self.ax[2, 0].clear()
        sns.barplot(x=monthly_totals.index.strftime('%Y-%m'), y=monthly_totals['travail'], palette='Blues_d', ax=self.ax[2, 0])

        self.ax[2, 0].set_xlabel('Mois')
        self.ax[2, 0].set_ylabel('Moyenne Travail (heures)')
        self.ax[2, 0].set_title('Moyenne Travail par Mois')

        # s'assurer que la liste `patches` est remplie avant de surligner les barres
        if len(self.ax[2, 0].patches) > 0:
            highest_day = grouped.idxmax()
            lowest_day = grouped.idxmin()
            try:
                highest_idx = grouped.index.get_loc(highest_day)
                lowest_idx = grouped.index.get_loc(lowest_day)
                self.ax[2, 0].patches[highest_idx].set_facecolor('green')
                self.ax[2, 0].patches[lowest_idx].set_facecolor('red')
            except IndexError:
                pass  # gérer le cas où les indices sont hors de la plage

        # ajouter des infobulles interactives pour le graphique en barres
        if hasattr(self.ax[2, 0], 'patches') and len(self.ax[2, 0].patches) > 0:
            mplcursors.cursor(self.ax[2, 0].patches, hover=True).connect(
                "add", lambda sel: sel.annotation.set_text(f'{monthly_totals.index[sel.index].strftime("%Y-%m")}: {monthly_totals["travail"].iloc[sel.index]:.1f} heures')
            )

        # tracer le nombre de jours de travail par mois
        days_of_travail = monthly_totals['travail'] / 8  # convertir les heures en jours

        self.ax[2, 1].clear()
        sns.lineplot(x=monthly_totals.index, y=days_of_travail, marker='o', color='blue', ax=self.ax[2, 1])

        max_days = days_of_travail.max()
        min_days = days_of_travail.min()
        max_date_days = days_of_travail.idxmax()
        min_date_days = days_of_travail.idxmin()
        self.ax[2, 1].plot(max_date_days, max_days, 'go', markersize=10, label='Max Jours de Travail')
        self.ax[2, 1].plot(min_date_days, min_days, 'ro', markersize=10, label='Min Jours de Travail')

        self.ax[2, 1].set_xlabel('Mois')
        self.ax[2, 1].set_ylabel('Nombre de Jours de Travail')
        self.ax[2, 1].set_title('Nombre de Jours de Travail par Mois')

        # graphique en anneau montrant le nombre d'heures de travail par rapport aux heures prévues
        expected_hours_per_week = 40
        actual_hours = self.filtered_df['travail'].mean() * len(pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max(), freq='D')) / 7
        total_weeks = len(pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max(), freq='W'))

        expected_hours = expected_hours_per_week * total_weeks
        actual_hours = max(0, actual_hours)
        expected_hours = max(0, expected_hours)

        self.ax[0, 1].clear()
        if expected_hours > 0:
            wedges, texts, autotexts = self.ax[0, 1].pie(
                [actual_hours, expected_hours - actual_hours],
                labels=['Heures Réelles', 'Heures Attendues'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#1887f5', '#fa0707'],
                wedgeprops=dict(width=0.3) 
            )

        if 'nom' in self.filtered_df.columns:
            employee_totals = self.filtered_df.groupby('nom')['travail'].sum()
            most_worked_employee = employee_totals.idxmax()
            least_worked_employee = employee_totals.idxmin()

            self.ax[0, 0].clear()
            self.ax[0, 0].text(0.5, 0.6, f"Employé le Plus Travaillé: {most_worked_employee}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax[0, 0].transAxes, fontsize=12, color='green')
            self.ax[0, 0].text(0.5, 0.4, f"Employé le Moins Travaillé: {least_worked_employee}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax[0, 0].transAxes, fontsize=12, color='red')
            self.ax[0, 0].set_title('Employés Travaillés')

            self.ax[0, 0].axis('off')            

        self.ax[0, 0].axis('off')

        plt.subplots_adjust(wspace=0.5, hspace=0.5)
        self.canvas.draw()

if __name__ == "__main__":
    app = QWidget(sys.argv)
    window = Dashboard ()
    window.showMaximized()
    sys.exit(app.exec_())
