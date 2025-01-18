# HR Data Generator Web Application

## Overview
This web application allows users to generate realistic HR datasets for multiple months. Users can customise various parameters to ensure the generated data meets their specific requirements. The app supports multiple languages for dataset generation, providing a flexible and intuitive interface for HR professionals, researchers, and developers.

## Features

### User Interface and Experience
- **User Instructions**: Clear guidelines at the top of the app explaining its usage.
- **Customisable Parameters**:
  - Number of months
  - Employee count per month (min: 100, max: 500).
  - Selectable fields (e.g., emp_id, emp_name, age, gender, organisation levels, position name, salary, hire/resignation dates, engagement score, performance result, marital status, etc.).
  - Age range and salary range.
  - Department and organisational fields.
- **Language Selection**: Supports multiple languages (e.g., English, Japanese) using Faker locales.
- **Side Job Records**: Option to include random side job records for a subset of employees.

### Data Generation
- **Realistic Data**: Utilises Faker library and custom logic to create locale-specific, realistic HR datasets.
- **Field Descriptions**: Each field includes a description or tooltip explaining its purpose.

### Data Output
- **Data Preview**: Displays a partial preview of the generated data in a table.
- **Download Options**: Provides downloads in CSV, Excel, and JSON formats.
- **No Visualisation**: The application focuses solely on data generation and download, without charts or metrics.

## File Structure
- **main.py**: Main application script.
- **requirements.txt**: List of dependencies.
- **README.md**: Project documentation.
- **JP_README.md**: Project documentation in Japanese.

## Licence
TBC

## Acknowledgements
- [Streamlit](https://streamlit.io/) for the interactive UI framework.
- [Faker](https://faker.readthedocs.io/en/master/) for data generation.
