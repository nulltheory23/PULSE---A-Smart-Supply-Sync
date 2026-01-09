import pandas as pd

# Show all columns & full width in console
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Hospital data
data = [
    {
        "Hospital Name": "Govt Medical College Hospital, Nilgiris",
        "Location": "Indhu Nagar, Mysore Road, Ooty, The Nilgiris, TN - 643005",
        "Email": "gmcnilgiris@gmail.com",
        "Telephone": "0423-2442212",
        "Oxygen Cylinders": 72,
        "Blood Supply": {"A+": 15, "B+": 12, "AB+": 6, "O+": 20, "O-": 4},
        "Anesthesia Machines": 5,
        "Sterilizers": 8,
        "Surgical Tables": 12
    },
    {
        "Hospital Name": "Government Lawley Hospital, Coonoor",
        "Location": "Mount Road, Coonoor Bazaar, Coonoor, The Nilgiris, TN - 643101",
        "Email": "ghcoonoorrbb@gmail.com",
        "Telephone": "0423-2231050",
        "Oxygen Cylinders": 45,
        "Blood Supply": {"A+": 10, "B+": 7, "AB+": 4, "O+": 18, "O-": 2},
        "Anesthesia Machines": 3,
        "Sterilizers": 6,
        "Surgical Tables": 9
    },
    {
        "Hospital Name": "Kotagiri Government Hospital, Kotagiri",
        "Location": "Kotagiri, Nilgiris District, Tamil Nadu",
        "Email": "kotagirigh@gmail.com",
        "Telephone": "04266-271309",
        "Oxygen Cylinders": 38,
        "Blood Supply": {"A+": 8, "B+": 5, "AB+": 3, "O+": 15, "O-": 2},
        "Anesthesia Machines": 2,
        "Sterilizers": 4,
        "Surgical Tables": 7
    },
    {
        "Hospital Name": "Gudalur Govt Hospital, Gudalur",
        "Location": "Gudalur, The Nilgiris District, Tamil Nadu - 643212",
        "Email": "gudalurgh@gmail.com",
        "Telephone": "04262-296366",
        "Oxygen Cylinders": 50,
        "Blood Supply": {"A+": 12, "B+": 9, "AB+": 4, "O+": 22, "O-": 3},
        "Anesthesia Machines": 4,
        "Sterilizers": 6,
        "Surgical Tables": 10
    },
    {
        "Hospital Name": "Panthalur Medical Hospital, Nilgiris",
        "Location": "Panthalur Main Road, The Nilgiris, Tamil Nadu",
        "Email": "panthalurgh@gmail.com",
        "Telephone": "0423-2552812",
        "Oxygen Cylinders": 41,
        "Blood Supply": {"A+": 9, "B+": 6, "AB+": 4, "O+": 18, "O-": 2},
        "Anesthesia Machines": 3,
        "Sterilizers": 5,
        "Surgical Tables": 8
    }
]

# Convert to DataFrame and expand Blood Supply
df = pd.json_normalize(data, sep='_')

# Clean column names
df.columns = df.columns.str.replace('Blood Supply_', '')

# Display DataFrame
print("\n=== Hospital Resource Data ===\n")
print(df)
print("\nRows:", df.shape[0], "Columns:", df.shape[1])