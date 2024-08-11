# Importation des modules nécessaires pour le projet
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QTableView, QMessageBox, QSizePolicy, QDialog)
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QColor
import pandas as pd
from openpyxl import load_workbook  # Pour manipuler les fichiers Excel
import psycopg2  # Pour se connecter à PostgreSQL
from config import config  # Notre fichier de config pour la DB
import sys
import os
from dashboard import Dashboard  # Notre tableau de bord (Tableau de bord, ça fait pro!)

# Modèle Pandas pour afficher les données dans QTableView
class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super(PandasModel, self).__init__()
        self.df = df  # On sauvegarde notre DataFrame

    def rowCount(self, parent=None):
        return len(self.df)  # Nombre de lignes

    def columnCount(self, parent=None):
        return len(self.df.columns)  # Nombre de colonnes

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self.df.iloc[index.row(), index.column()])  # Afficher les valeurs des cellules
        if role == Qt.BackgroundRole and index.column() == 2:
            return QColor(220, 220, 255)  # Une couleur sympa pour la 3ème colonne
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]  # Noms des colonnes
            else:
                return str(section + 1)  # Numéro de ligne
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            col_name = self.df.columns[index.column()]  # Nom de la colonne actuelle
            if col_name == 'Commentaire':
                self.df.iat[index.row(), index.column()] = value
                self.dataChanged.emit(index, index)  # Avertir que les données ont changé
                return True
            elif col_name == 'Travail':
                try:
                    # Convertir le temps de travail en hh:mm
                    new_time = pd.to_timedelta(value + ':00')
                    time_str = str(new_time).split()[2][:5]  # Extraire le format hh:mm
                    self.df.iat[index.row(), index.column()] = time_str
                    self.update_cumulative_travail(start_index=index.row())  # Mettre à jour le temps cumulé
                    self.dataChanged.emit(index, index)
                    return True
                except ValueError:
                    return False
            elif col_name == 'Date':
                try:
                    # Conversion de la date en yyyy-mm-dd
                    new_date = pd.to_datetime(value, format='%Y-%m-%d', errors='coerce')
                    if pd.notna(new_date):
                        self.df.iat[index.row(), index.column()] = new_date.strftime('%Y-%m-%d')
                        self.update_cumulative_travail(start_index=index.row())  # Mettre à jour le temps cumulé
                        self.dataChanged.emit(index, index)
                        return True
                    else:
                        return False
                except Exception as e:
                    print(f"Erreur lors de la mise à jour de la colonne Date: {e}")
                    return False
        return False

    def update_cumulative_travail(self, start_index=0):
        # On initialise le temps cumulé
        cumulative_time = pd.Timedelta(0)  

        for index, row in self.df.iterrows():
            if index < start_index:
                # Sauter les lignes avant l'index de départ
                cumulative_time = pd.to_timedelta(row['Travail Cumulée'] + ':00')
                continue

            if row['Travail'] == 'Abs':
                self.df.at[index, 'Travail Cumulée'] = cumulative_time
            else:
                try:
                    travail = pd.to_timedelta(row['Travail'] + ':00')
                    cumulative_time += travail
                    self.df.at[index, 'Travail Cumulée'] = cumulative_time
                except ValueError:
                    self.df.at[index, 'Travail Cumulée'] = cumulative_time

        # Formatage de la colonne 'Travail Cumulée' en hh:mm
        self.df['Travail Cumulée'] = self.df['Travail Cumulée'].apply(lambda x: str(x).split()[-1] if pd.notna(x) else '00:00')


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.df.columns[index.column()] in ['Commentaire', 'Travail', 'Date']:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def get_dataframe(self):
        return self.df  # Retourne notre DataFrame

# Classe pour manipuler les fichiers Excel
class ExcelFileHandler:
    def __init__(self):
        self.df = pd.DataFrame()

    def connect_db(self):
        try:
            params = config()
            connection = psycopg2.connect(**params)
            print("Connexion à la base de données réussie")
            return connection
        except Exception as error:
            print(f"Erreur de connexion à la base de données: {error}")
            return None

    def load_excel(self, file_path):
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path, engine='openpyxl')
                elif file_path.endswith('.xls'):
                    df = pd.read_excel(file_path, engine='xlrd')
                else:
                    print(f"Format de fichier non pris en charge: {file_path}")
                    return None

                print(f"Fichier chargé: {file_path}")
                print("DataFrame initial:")
                print(df.head())  # Afficher les premières lignes pour vérifier les données

                if all(col in df.columns for col in ['Entrée.', 'Sortie.', 'Nom.']):
                    extracted_data = []
                    cumulative_diff = pd.Timedelta(0)
                    formatted_cum_diff = '00:00:00'

                    for _, row in df.iterrows():
                        Entrée = pd.to_datetime(row['Entrée.'], errors='coerce')
                        Sortie = pd.to_datetime(row['Sortie.'], errors='coerce')
                        Nom = row['Nom.']
                        Date = pd.to_datetime(row['Date.'], errors='coerce')

                        print(f"Traitement de la ligne: Entrée={Entrée}, Sortie={Sortie}, Nom={Nom}")  

                        if pd.notna(Entrée) and pd.notna(Sortie):
                            time_diff = Sortie - Entrée
                            total_seconds = int(time_diff.total_seconds())
                            diff_hours = total_seconds // 3600
                            diff_minutes = (total_seconds % 3600) // 60
                            diff_seconds = total_seconds % 60
                            formatted_diff = f"{diff_hours:02}:{diff_minutes:02}:{diff_seconds:02}"

                            cumulative_diff += time_diff
                            cumulative_total_seconds = int(cumulative_diff.total_seconds())
                            cum_hours = cumulative_total_seconds // 3600
                            cum_minutes = (cumulative_total_seconds % 3600) // 60
                            cum_seconds = cumulative_total_seconds % 60
                            formatted_cum_diff = f"{cum_hours:02}:{cum_minutes:02}:{cum_seconds:02}"

                            extracted_data.append({
                                'Entrée': Entrée.strftime('%H:%M:%S'),
                                'Sortie': Sortie.strftime('%H:%M:%S'),
                                'Nom': Nom,
                                'Date': Date.strftime('%Y-%m-%d'),
                                'Travail': formatted_diff,
                                'Travail Cumulée': formatted_cum_diff,
                                'Commentaire': ''  
                            })
                        else:
                            extracted_data.append({
                                'Entrée': 'Abs',
                                'Sortie': 'Abs',
                                'Nom': Nom,
                                'Date': 'Abs',
                                'Travail': 'Abs',
                                'Travail Cumulée': formatted_cum_diff,
                                'Commentaire': '' 
                            })

                    extracted_df = pd.DataFrame(extracted_data)
                    reordered_columns = ['Nom', 'Date', 'Entrée', 'Sortie', 'Travail', 'Travail Cumulée', 'Commentaire']
                    extracted_df = extracted_df[reordered_columns]

                    print("Lignes extraites et converties:")
                    print(extracted_df)

                    self.df = extracted_df 

                    return extracted_df
                else:
                    print("Les colonnes requises ne sont pas présentes dans la DataFrame.")
                    return None
            except Exception as e:
                print(f"Erreur lors du chargement du fichier {file_path}: {e}")
                return None
        else:
            print(f"Le fichier {file_path} n'existe pas.")
            return None 

    def save_excel(self, df, output_file_path):
        try:
            df.to_excel(output_file_path, index=False)
            wb = load_workbook(output_file_path)
            ws = wb.active
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 15
            ws.column_dimensions['E'].width = 15
            ws.column_dimensions['F'].width = 15
            ws.column_dimensions['G'].width = 40
            wb.save(output_file_path)
            print(f"Fichier enregistré sous: {output_file_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier: {e}")

    def insert_into_db(self, df):
        try:
            connection = self.connect_db()
            if connection:
                cursor = connection.cursor()
                for _, row in df.iterrows():
                    cursor.execute("INSERT INTO work_data (name, date, start_time, end_time, work_time, cumulative_work_time, comments) "
                                   "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                   (row['Nom'], row['Date'], row['Entrée'], row['Sortie'], row['Travail'], row['Travail Cumulée'], row['Commentaire']))
                connection.commit()
                print("Les données ont été insérées dans la base de données.")
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Erreur lors de l'insertion des données dans la base: {e}")

    def get_dataframe(self):
        return self.df  

# Pour un usage dans une application PyQt5
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Data Processor")
        self.resize(1000, 600)  
        self.excel_handler = ExcelFileHandler()
        self.model = PandasModel()
        self.initUI()

    def initUI(self):
        openButton = QPushButton("Ouvrir un fichier Excel")  
        openButton.clicked.connect(self.openFileDialog)

        saveButton = QPushButton("Enregistrer dans un fichier Excel") 
        saveButton.clicked.connect(self.saveFileDialog)

        insertButton = QPushButton("Insérer dans la base de données")  
        insertButton.clicked.connect(self.insertIntoDB)

        dashboardButton = QPushButton("Afficher le tableau de bord")  
        dashboardButton.clicked.connect(self.showDashboard)

        layout = QVBoxLayout() 
        layout.addWidget(openButton)
        layout.addWidget(saveButton)
        layout.addWidget(insertButton)
        layout.addWidget(dashboardButton)

        table = QTableView()  
        table.setModel(self.model)

        mainLayout = QHBoxLayout()  
        mainLayout.addLayout(layout)
        mainLayout.addWidget(table)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def openFileDialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier Excel", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
        if file_path:
            df = self.excel_handler.load_excel(file_path)
            if df is not None:
                self.model = PandasModel(df)
                self.model.layoutChanged.emit()

    def saveFileDialog(self):
        options = QFileDialog.Options()
        output_file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if output_file_path:
            self.excel_handler.save_excel(self.model.get_dataframe(), output_file_path)

    def insertIntoDB(self):
        reply = QMessageBox.question(self, "Confirmer l'insertion", "Êtes-vous sûr de vouloir insérer ces données dans la base de données?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            df = self.model.get_dataframe()
            self.excel_handler.insert_into_db(df)

    def showDashboard(self):
        dashboard_dialog = QDialog(self)
        dashboard_dialog.setWindowTitle("Tableau de bord")  
        dashboard_layout = QVBoxLayout()
        dashboard = Dashboard() 
        dashboard_layout.addWidget(dashboard)
        dashboard_dialog.setLayout(dashboard_layout)
        dashboard_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
