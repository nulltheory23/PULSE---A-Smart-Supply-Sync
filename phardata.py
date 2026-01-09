import pandas as pd

# Display settings to avoid truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Pharmacy data
data = [
    {
        "Pharmacy Name": "Lakshmi Pharmacy",
        "Location": "Indhuja Nagar, Joo Main Road, Nilgiris, Tamil Nadu",
        "Email Address": "lakshmi.pharmacy@gmail.com",
        "Telephone Number": "9876543210",
        "Oxygen Cylinders Available": 18,
        "Blood Supplies": {"A+": 10, "B+": 8, "AB+": 4, "O+": 12, "O-": 3},
        "Anesthesia Machines": 2,
        "Sterilizers": 3,
        "Surgical Tables": 5
    },
    {
        "Pharmacy Name": "Gowtham Medicals",
        "Location": "Thillai Nagar, Ram Main Road, Nilgiris, Tamil Nadu",
        "Email Address": "gowtham.medicals@gmail.com",
        "Telephone Number": "9123456780",
        "Oxygen Cylinders Available": 25,
        "Blood Supplies": {"A+": 12, "B+": 9, "AB+": 5, "O+": 15, "O-": 4},
        "Anesthesia Machines": 3,
        "Sterilizers": 4,
        "Surgical Tables": 6
    },
    {
        "Pharmacy Name": "Selvam Pharmacy",
        "Location": "Udhaiyamadalam, Udhai Main Road, Nilgiris, Tamil Nadu",
        "Email Address": "sujeeth.pharmacy@gmail.com",
        "Telephone Number": "9345678120",
        "Oxygen Cylinders Available": 14,
        "Blood Supplies": {"A+": 8, "B+": 6, "AB+": 3, "O+": 10, "O-": 2},
        "Anesthesia Machines": 1,
        "Sterilizers": 2,
        "Surgical Tables": 4
    },
    {
        "Pharmacy Name": "Phoenix Medicals",
        "Location": "Don Cross, Coonoor, Nilgiris",
        "Email Address": "phoenix.medicals@gmail.com",
        "Telephone Number": "9567812340",
        "Oxygen Cylinders Available": 30,
        "Blood Supplies": {"A+": 15, "B+": 11, "AB+": 6, "O+": 18, "O-": 5},
        "Anesthesia Machines": 4,
        "Sterilizers": 5,
        "Surgical Tables": 7
    },
    {
        "Pharmacy Name": "None Pharmacy",
        "Location": "Panthalur–Coonoor Main Road, Nilgiris",
        "Email Address": "none.pharmacy@gmail.com",
        "Telephone Number": "9786541230",
        "Oxygen Cylinders Available": 10,
        "Blood Supplies": {"A+": 6, "B+": 5, "AB+": 2, "O+": 8, "O-": 1},
        "Anesthesia Machines": 1,
        "Sterilizers": 2,
        "Surgical Tables": 3
    }
]

# Convert to DataFrame and expand nested Blood Supplies
df = pd.json_normalize(data, sep='_')

# Clean column names
df.columns = df.columns.str.replace('Blood Supplies_', '')

# Display final table
print("\n=== Pharmacy Resource Table ===\n")
print(df)
print("\nTotal Rows:", df.shape[0])
print("Total Columns:", df.shape[1])