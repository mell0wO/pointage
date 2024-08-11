# Dashboard for Work Hours Analysis

This project provides a graphical dashboard for analyzing work hours data. It allows users to filter data by month and employee name and visualize various aspects of work hours through interactive charts using Matplotlib and PyQt5.

## Features

- **Interactive Filters:** Easily select the month and employee name to filter the data.
- **Visualizations:**
  - Total work hours by day of the week.
  - Work hours over time with highlights for peak and low values.
  - Total work hours by month.
  - Number of work days per month.
  - Comparison of actual work hours against expected hours.
  - Employee work hours summary.

## Requirements

To run this project, you'll need the following Python packages:

- Python 3.x
- PyQt5
- Pandas
- Matplotlib
- mplcursors
- SQLAlchemy
- PostgreSQL (for database connection)

You can install the necessary packages using pip:

```bash
pip install pandas matplotlib mplcursors sqlalchemy psycopg2-binary pyqt5
```

# Project Title

A brief description of what this project does and who it's for.

## Setup

### 1. Database Configuration

- Ensure you have PostgreSQL running.
- Create a database named `bi`.
- Create a table named `dbbi` with the following columns:
  - `date` (Date)
  - `nom` (Employee Name)
  - `travail` (Work Hours)

### 2. Update Database Connection

- Modify the database connection string in the `load_and_process_data()` function if necessary:

```python
engine = create_engine('postgresql://username:password@localhost:5432/bi')
```
## Usage

### Filters

- Use the dropdown menus to select the month and employee name.
- Click "Apply Filter" to update the charts.

### Charts

1. **Total Work Hours by Day of the Week:** Displays the total hours worked on each day of the week.
2. **Work Hours Over Time with Special Markers:** Shows the work hours over time, highlighting special markers.
3. **Total Work Hours by Month:** Visualizes the total work hours for each month.
4. **Number of Work Days per Month:** Illustrates the number of days worked each month.
5. **Actual vs Expected Work Hours:** Compares the actual hours worked against the expected hours.
6. **Work Hours Summary for Employees:** Summarizes the total work hours for each employee.

## Troubleshooting

### Database Issues

- Ensure the PostgreSQL database is correctly configured and accessible.

### Data Issues

- Verify that the table `dbbi` contains the expected columns and data.


