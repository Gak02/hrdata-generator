import streamlit as st
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="HR Data Generator",
    page_icon="👥",
    layout="wide"
)

# Application title and description
st.title("🪄 HR Data Generator")
st.markdown("""
This application generates sample HR data for one month with realistic employee information.
You can customise various parameters and download the generated dataset in multiple formats.
""")

# Field names and its description
fields = [
    "Employee ID",
    "Name",
    "Age",
    "Gender",
    "Organisation",
    "Position",
    "Salary",
    "Hire Date",
    "Resign Date",
    "Engagement Score",
    "Performance",
    "Marital Status",
    "Address",
    "Emp Type",
    "Job Category",
    "Job Grade"
]

descriptions = [
    "Unique identifier for each employee",
    "Full name of the employee",
    "Employee's age",
    "Employee's gender identity",
    "Four-level organisational hierarchy",
    "Job title/role",
    "Annual salary in USD",
    "Employment start date",
    "Employment end date (if applicable)",
    "Employee engagement score",
    "Annual performance result",
    "Whether the employee is married",
    "Employee's address",
    "Type of employment (e.g., full-time, contract etc)",
    "Functional or professional category for the job",
    "Grade or level of the job within the company"
]

# Create data frame
data = {"Field": fields, "Description": descriptions}
df = pd.DataFrame(data)

# Display field descriptions on the main body
st.subheader("Field Descriptions")
st.table(df)

# Sidebar for parameters
st.sidebar.header("⚙️ Configuration")

# Language selection
languages = {
    "English": "en_US",
    "Japanese": "ja_JP"
}
selected_language = st.sidebar.selectbox(
    "Select Language",
    list(languages.keys())
)

# Initialize Faker with selected locale
fake = Faker(languages[selected_language])

# Employee count selection
employee_count = st.sidebar.slider(
    "Number of Employees",
    min_value=200,
    max_value=500,
    value=300,
    help="Select the number of employees to generate data for"
)

# Field selection
st.sidebar.subheader("Select Fields to Include")
include_fields = {
    "Employee ID": st.sidebar.checkbox("Employee ID", value=True),
    "Name": st.sidebar.checkbox("Name", value=True),
    "Age": st.sidebar.checkbox("Age", value=True),
    "Gender": st.sidebar.checkbox("Gender", value=True),
    "Organisation": st.sidebar.checkbox("Organisation Hierarchy", value=True),
    "Position": st.sidebar.checkbox("Position", value=True),
    "Salary": st.sidebar.checkbox("Salary", value=True),
    "Hire Date": st.sidebar.checkbox("Hire Date", value=True),
    "Resign Date": st.sidebar.checkbox("Resign Date", value=True),
    "Engagement Score": st.sidebar.checkbox("Engagement Score", value=True),
    "Performance": st.sidebar.checkbox("Performance Result", value=True),
    "Marital Status": st.sidebar.checkbox("Marital Status", value=True),
    "Address": st.sidebar.checkbox("Address", value=True),
    "Emp Type": st.sidebar.checkbox("Emp Type", value=True),
    "Job Category": st.sidebar.checkbox("Job Category", value=True),
    "Job Grade": st.sidebar.checkbox("Job Grade", value=True)
}

# Additional parameters
st.sidebar.subheader("Additional Parameters")
age_range = st.sidebar.slider(
    "Age Range",
    min_value=18,
    max_value=65,
    value=(25, 55)
)

salary_range = st.sidebar.slider(
    "Salary Range (JPY)",
    min_value=3000000,
    max_value=30000000,
    value=(4000000, 10000000)
)

include_side_jobs = st.sidebar.checkbox(
    "Include subaffiliated jobs",
    value=False,
    help="Generate additional subaffiliated job records for some employees"
)

# Organisation hierarchy
organisations = {
    "org_lv1": ["Sample inc."],
    "org_lv2": ["Sales&Marketing", "Engineering", "HR", "Finance"],
    "org_lv4": ["Team A", "Team B", "Team C", "Team D", "Team E"],
}

# Define org_lv2 weights
org_lv2_weights = [4, 3, 1.5, 1.5]
org_lv2_choices = ["Sales", "Engineering", "HR", "Finance"]

# Define org_lv3 mapping based on org_lv2
departments = {
    "Sales": ["Advertising", "Market Research", "Customer Relations", "Sales Operations"],
    "Marketing": ["Advertising", "Market Research", "Customer Relations", "Sales Operations"],
    "Engineering": ["Software Development", "Quality Assurance", "Product Design", "DevOps"],
    "HR": ["Recruitment", "Employee Relations", "Training & Development", "Compensation & Benefits"],
    "Finance": ["Accounting", "Budgeting", "Financial Planning", "Internal Audit"]
}

positions = [
    "Staff", "Team Lead",
    "Manager", "General Manager",
    "VP", "C-Level"
]

# Define position hierarchy and corresponding salary multiplier
position_hierarchy = {
"Staff": 1,
"Team Lead": 1.2,
"Manager": 1.5,
"General Manager": 2,
"VP": 2.5,
"C-Level": 3
}

# Define position weights
position_weights = [5, 3, 1, 0.6, 0.3, 0.1]
position_choices = ["Staff", "Team Lead", "Manager", "General Manager", "VP", "C-Level"]

# Define engagement score thresholds for performance levels
performance_levels = {
    "S": 90,
    "A": 75,
    "B": 50,
    "C": 0
}

# emp type list and define weights
employee_types = ["full-time", "contract", "outsourced"]
emp_type_weights = [6, 3, 1]

# job category list
sales_marketing = ["Sales", "Marketing", "Customer Success"]
engineering = ["Software Engineering", "Data Science / Data Engineering", "IT Infrastructure / Cloud"]
hr_category = ["HR"]
finance = ["Finance / Accounting", "Business Planning", "Internal Audit / Compliance"]

# List of capitals and non-capitals
capitals = ["Tokyo", "Kanagawa", "Saitama"]
non_capitals = ["Hyogo", "Kyoto", "Ibaraki", "Hiroshima", "Osaka", "Aichi", "Hokkaido", "Fukuoka"]

# job grade mapping
position_to_grade = {
    "Staff": "Lv1",
    "Team Lead": "Lv2",
    "Manager": "Lv3",
    "General Manager": "Lv4",
    "VP": "Lv5",
    "C-Level": "Lv6"
}

def generate_employee_data():
    """Generate employee data based on selected parameters"""
    data = []
    current_date = datetime.now()

    for i in range(employee_count):
        employee = {}

        if include_fields["Employee ID"]:
            employee["emp_id"] = f"EMP{str(i+1).zfill(6)}"

        if include_fields["Name"]:
            employee["name"] = fake.name()

        if include_fields["Age"]:
            employee["age"] = random.randint(age_range[0], age_range[1])

        if include_fields["Gender"]:
            employee["gender"] = random.choice(["Male", "Female", "Other"])

        if include_fields["Organisation"]:
            employee["org_lv1"] = random.choice(organisations["org_lv1"])
            employee["org_lv2"] = random.choices(org_lv2_choices, weights=org_lv2_weights, k=1)[0]
            # Generate org_lv3 based on org_lv2
            org_lv2 = employee["org_lv2"]
            employee["org_lv3"] = random.choice(departments.get(org_lv2, ["General"]))
            employee["org_lv4"] = random.choice(organisations["org_lv4"])

        if include_fields["Position"]:
            # Assign position based on weighted random selection
            employee["position"] = random.choices(position_choices, weights=position_weights, k=1)[0]

        if include_fields["Salary"]:
            # Set salary based on position
            position = employee.get("position", "Staff")
            base_salary = random.uniform(salary_range[0], salary_range[1])
            multiplier = position_hierarchy.get(position, 1)
            employee["salary"] = round(base_salary * multiplier, -3)

        if include_fields["Hire Date"]:
            max_years_ago = 20
            days_ago = random.randint(0, 365 * max_years_ago)
            employee["hire_date"] = (current_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        if include_fields["Resign Date"]:
            if random.random() < 0.05:  # 5% chance of resignation
                resign_days = random.randint(1, 30)  # Resign within the next month
                employee["resign_date"] = (current_date + timedelta(days=resign_days)).strftime("%Y-%m-%d")
            else:
                employee["resign_date"] = None

        if include_fields["Engagement Score"]:
            employee["engagement_score"] = round(random.uniform(14, 100), 0)

        if include_fields["Performance"]:
            # Assign performance based on engagement score
            engagement_score = employee.get("engagement_score", random.uniform(0, 100))
            for level, threshold in performance_levels.items():
                if engagement_score >= threshold:
                    employee["performance"] = level
                    break

        if include_fields["Marital Status"]:
            employee["is_married"] = random.choice([True, False])

        if include_fields.get("Address"):
            # 80% from capitals、20% from non-capitals
            if random.random() < 0.8:
                city = random.choice(capitals)
            else:
                city = random.choice(non_capitals)

            employee["address"] = city

        if include_fields.get("Emp Type"):
            employee["emp_type"] = random.choices(employee_types, weights=emp_type_weights, k=1)[0]

        if include_fields.get("Job Category"):
            org_lv2 = employee.get("org_lv2", "")
            if org_lv2 == "Sales&Marketing":
                employee["job_category"] = random.choice(sales_marketing)
            elif org_lv2 == "Engineering":
                employee["job_category"] = random.choice(engineering)
            elif org_lv2 == "HR":
                employee["job_category"] = random.choice(hr_category)
            elif org_lv2 == "Finance":
                employee["job_category"] = random.choice(finance)
            else:
                employee["job_category"] = "General"

        if include_fields.get("Job Grade"):
            position = employee.get("position", "Staff")
            employee["job_grade"] = position_to_grade.get(position, "Lv1")

        # Nullify Organisation fields for specific positions
        position = employee.get("position")
        if position == "C-Level":
            employee["org_lv2"] = None
            employee["org_lv3"] = None
            employee["org_lv4"] = None
        elif position == "VP":
            employee["org_lv3"] = None
            employee["org_lv4"] = None

        data.append(employee)

        # Generate subaffiliated job records (兼務)
        if include_side_jobs and random.random() < 0.35 and position in ["Staff", "Manager", "General Manager"]:
            concurrent_job = employee.copy()
            concurrent_job["emp_id"] = f"{concurrent_job['emp_id']}_sub"
            # Change only org_lv3 and org_lv4 for the concurrent job
            concurrent_job["org_lv3"] = random.choice(departments.get(org_lv2, ["General"]))
            concurrent_job["org_lv4"] = random.choice(organisations["org_lv4"])
            data.append(concurrent_job)

    return pd.DataFrame(data)


# Generate button
if st.button("Generate HR Data", type="primary"):
    # Generate data
    df = generate_employee_data()
    
    # Display preview
    st.subheader("Data Preview")
    st.dataframe(df.head(10))
    
    # Download buttons
    st.subheader("Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    # CSV download
    csv = df.to_csv(index=False)
    col1.download_button(
        label="Download CSV",
        data=csv,
        file_name="hr_data.csv",
        mime="text/csv"
    )
    
    # Excel download
    from io import BytesIO
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    excel_data = excel_buffer.getvalue()
    col2.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="hr_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # JSON download
    json = df.to_json(orient="records")
    col3.download_button(
        label="Download JSON",
        data=json,
        file_name="hr_data.json",
        mime="application/json"
    )

# Add tooltips and documentation
st.sidebar.markdown("---")

st.sidebar.markdown("""
### Contact
- **email**: hrdata.generator@gmail.com
- **X account**: @hrdata_gen
""")
