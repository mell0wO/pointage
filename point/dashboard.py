import sys
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton, QHBoxLayout
from sqlalchemy import create_engine
from matplotlib.dates import DateFormatter

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jour de la Semaine vs Travail")
        self.setGeometry(100, 100, 1200, 800)
        # créer la mise en page principale
        self.layout = QVBoxLayout(self)

        # créer une mise en page pour le filtre de sélection du mois et du nom
        self.filter_layout = QHBoxLayout()
        self.layout.addLayout(self.filter_layout)

        # menu déroulant de sélection du mois
        self.month_combobox = QComboBox()
        self.month_combobox.addItem("Tous les mois")
        for month in range(1, 13):
            self.month_combobox.addItem(f"{month:02d}")
        self.filter_layout.addWidget(self.month_combobox)

        # menu déroulant de sélection du nom
        self.name_combobox = QComboBox()
        self.name_combobox.addItem("Tous les noms")  # Placeholder item
        self.filter_layout.addWidget(self.name_combobox)

        # bouton d'application du filtre
        self.apply_button = QPushButton("Appliquer le Filtre")
        self.apply_button.clicked.connect(self.apply_filter)
        self.filter_layout.addWidget(self.apply_button)

        # créer la figure et les axes de matplotlib
        self.figure, self.ax = plt.subplots(3, 2, figsize=(12, 18))  # Trois lignes, deux colonnes

        # créer le canvas et l'ajouter à la mise en page
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)

        # charger et traiter les données
        self.load_and_process_data()

        # initialiser filtered_df avec l'ensemble complet des données
        self.filtered_df = self.df

        # tracer les données
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

            # remplir le combobox des noms avec les valeurs de 'nom'
            if 'nom' in self.df.columns:
                noms = self.df['nom'].dropna().unique()  # supprimer les valeurs NaN et obtenir les noms uniques
                cleaned_noms = [nom.strip() for nom in noms] # supprimer les espaces au début/à la fin
                unique_noms = sorted(set(cleaned_noms)) # supprimer les doublons et trier
                self.name_combobox.clear()  # vider les éléments existants
                self.name_combobox.addItems(["Tous les noms"] + unique_noms)  # ajouter des éléments au combobox
            else:
                print("Column 'nom' does not exist in the DataFrame.")

            # s'assurer que la colonne 'date' est au format datetime
                if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

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
            # obtenir le mois et le nom sélectionnés depuis les comboboxes
            selected_month = self.month_combobox.currentText()
            selected_name = self.name_combobox.currentText()

            # convertir selected_month en entier si ce n'est pas "tous les mois"
            if selected_month != "Tous les mois":
                selected_month = int(selected_month)
            else:
                selected_month = None

            # filtrer par mois
            if 'date' in self.df.columns:
                if selected_month is not None:
                    # filtrer par mois
                    month_filtered_df = self.df[self.df['date'].dt.month == selected_month]
                else:
                    month_filtered_df = self.df

                # filter par nom
                if selected_name != "Tous les noms":
                    self.filtered_df = month_filtered_df[month_filtered_df['nom'] == selected_name]
                else:
                    self.filtered_df = month_filtered_df

                # afficher le DataFrame filtré pour le débogage
                print("Filtered DataFrame:\n", self.filtered_df)
            else:
                print("Column 'date' does not exist in the DataFrame.")
                self.filtered_df = pd.DataFrame()  # définir comme DataFrame vide si la colonne 'date' est manquante
            # re-tracer les données avec les filtres sélectionnés
            self.plot_data()

        except Exception as e:
            print(f"Erreur lors de l'application du filtre : {e}")
            self.filtered_df = pd.DataFrame()  # définir comme DataFrame vide en cas d'erreur

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

        # grouper par 'Jour_de_la_Semaine' et sommer le 'travail'
        grouped = filtered_df.groupby('Jour_de_la_Semaine')['travail'].sum().reindex(weekdays, fill_value=0)
        grouped.index = weekdays_fr 

        self.ax[0, 0].clear()
        bars = self.ax[0, 0].bar(grouped.index, grouped.values, color='skyblue')

        # mettre en surbrillance les valeurs les plus élevées et les plus basses
        highest_day = grouped.idxmax()
        lowest_day = grouped.idxmin()
        self.ax[0, 0].bar(highest_day, grouped.max(), color='green', edgecolor='black')
        self.ax[0, 0].bar(lowest_day, grouped.min(), color='red', edgecolor='black')
        
        self.ax[0, 0].set_xlabel('Jour de la Semaine')
        self.ax[0, 0].set_ylabel('Total Travail (heures)')
        self.ax[0, 0].set_title('Total Travail par Jour de la Semaine')

        # ajouter des infobulles interactives uniquement pour le graphique en barres
        mplcursors.cursor(bars, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f'{grouped.index[sel.index]}: {grouped.values[sel.index]:.1f} heures')
        )

        # tracer le travail pour chaque date, y compris les dates manquantes
        all_dates = pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max())
        full_df = pd.DataFrame({'date': all_dates})
        full_df = full_df.merge(self.filtered_df[['date', 'travail']], on='date', how='left').fillna({'travail': 0})
        self.ax[0, 1].clear()
        line = self.ax[0, 1].plot(full_df['date'], full_df['travail'], marker='o', color='blue')[0]

        # mettre en surbrillance les valeurs les plus élevées et les plus basses dans le graphique en ligne
        max_value = full_df['travail'].max()
        min_value = full_df['travail'].min()
        max_date = full_df.loc[full_df['travail'] == max_value, 'date'].iloc[0]
        min_date = full_df.loc[full_df['travail'] == min_value, 'date'].iloc[0]
        self.ax[0, 1].plot(max_date, max_value, 'go', markersize=10)  
        self.ax[0, 1].plot(min_date, min_value, 'ro', markersize=10) 
        
        # changer la couleur de la ligne pour indiquer le seuil
        self.ax[0, 1].plot(full_df['date'], full_df['travail'], color='blue')
        self.ax[0, 1].axhline(y=8, color='red', linestyle='--', label='Seuil de 8 heures')
  
        self.ax[0, 1].set_xlabel('Date')
        self.ax[0, 1].set_ylabel('Travail (heures)')
        self.ax[0, 1].set_title('Travail au Fil du Temps')
        self.ax[0, 1].xaxis.set_major_formatter(DateFormatter('%d-%m-%Y')))

        # tracer le total du travail par mois
        monthly_totals = self.filtered_df.groupby(self.filtered_df['date'].dt.to_period('M')).agg({'travail': 'sum'})
        monthly_totals.index = monthly_totals.index.to_timestamp()

        self.ax[1, 0].clear()
        bars = self.ax[1, 0].bar(monthly_totals.index.strftime('%Y-%m'), monthly_totals['travail'], color='skyblue')

        self.ax[1, 0].set_xlabel('Mois')
        self.ax[1, 0].set_ylabel('Total Travail (heures)')
        self.ax[1, 0].set_title('Total Travail par Mois')

        # ajouter des infobulles interactives uniquement pour le graphique en barres
        mplcursors.cursor(bars, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f'{monthly_totals.index[sel.index].strftime("%Y-%m")}: {monthly_totals["travail"].iloc[sel.index]:.1f} heures')
        )

        # tracer le nombre de jours de travail par mois
        days_of_travail = monthly_totals['travail'] / 8  # convertir les heures en jours

        self.ax[1, 1].clear()
        line = self.ax[1, 1].plot(days_of_travail.index, days_of_travail, marker='o', color='blue')[0]

        self.ax[1, 1].set_xlabel('Mois')
        self.ax[1, 1].set_ylabel('Nombre de Jours de Travail')
        self.ax[1, 1].set_title('Nombre de Jours de Travail par Mois')

        # graphique en anneau montrant le nombre d'heures de travail par rapport aux heures prévues
        expected_hours_per_week = 40
        actual_hours = self.filtered_df['travail'].sum()
        total_weeks = len(pd.date_range(start=self.filtered_df['date'].min(), end=self.filtered_df['date'].max(), freq='W'))

        expected_hours = expected_hours_per_week * total_weeks

        # s'assurer que les valeurs sont non négatives
        actual_hours = max(0, actual_hours)
        expected_hours = max(0, expected_hours)

        self.ax[2, 0].clear()
        if expected_hours > 0: 
            self.ax[2, 0].pie(
                [actual_hours, expected_hours - actual_hours],
                labels=['Heures Réelles', 'Heures Attendues'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#ff9999', '#66b3ff'],
                wedgeprops=dict(width=0.3)  # transformer le graphique circulaire en graphique en anneau
            )
            self.ax[2, 0].set_title('Heures Réelles vs Heures Attendues')
        else:
            self.ax[2, 0].text(0.5, 0.5, 'Pas d\'heures attendues à afficher',
                                horizontalalignment='center', verticalalignment='center',
                                transform=self.ax[2, 0].transAxes, fontsize=12, color='red')


        # employés avec les valeurs de travail les plus élevées et les plus basses
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
    app = QWidget(sys.argv)
    window = Dashboard ()
    window.showMaximized()
    sys.exit(app.exec_())
