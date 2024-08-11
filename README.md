*Dashboard for Work Hours Analysis*
This project provides a graphical dashboard to analyze work hours data. It allows users to filter data by month and employee name and visualize various aspects of work hours through interactive charts using Matplotlib and PyQt5.

Features
Interactive Filters: Select the month and employee name to filter the data.
Visualizations:
Total work hours by day of the week.
Work hours over time with highlights for peak and low values.
Total work hours by month.
Number of work days per month.
Comparison of actual work hours against expected hours.
Employee work hours summary.
Requirements
Python 3.x
PyQt5
Pandas
Matplotlib
mplcursors
SQLAlchemy
PostgreSQL (for database connection)
You can install the necessary Python packages using pip:

bash
Copier le code
pip install pandas matplotlib mplcursors sqlalchemy psycopg2-binary pyqt5
Setup
Database Configuration:

Ensure you have PostgreSQL running and a database named bi.
The database should have a table dbbi with columns date, nom, and travail.
Update Database Connection:

Modify the database connection string in load_and_process_data() method if necessary:
python
Copier le code
engine = create_engine('postgresql://username:password@localhost:5432/bi')
Running the Application:

Save the provided Python code in a file named dashboard.py.
Run the application using:
bash
Copier le code
python dashboard.py
Usage
Filters: Use the dropdown menus to select the month and employee name. Click "Apply Filter" to update the charts.
Charts:
The first chart shows total work hours by day of the week.
The second chart displays work hours over time with special markers.
The third chart visualizes total work hours by month.
The fourth chart illustrates the number of work days per month.
The fifth chart compares actual work hours against expected hours.
The sixth chart summarizes the work hours for employees.
Troubleshooting
Ensure the PostgreSQL database is correctly configured and accessible.
Verify that the table dbbi contains the expected columns and data.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request with your proposed changes.
