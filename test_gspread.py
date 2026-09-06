import gspread

# 1. Authenticate using your downloaded JSON key file
# Replace 'credentials.json' with your actual file name
gc = gspread.service_account(filename='ghanimurtafa-2506-5810e227e5e9.json')

# 2. Open the Google Sheet by its title
# (The Service Account MUST be added as an Editor to this sheet)
spreadsheet = gc.open("Keuangan Se-MoGa")

# 3. Select the specific tab (worksheet) you want to edit
# sheet1 selects the first tab, but you can also use worksheet("Tab Name")
worksheet = spreadsheet.worksheet("Coret2")  # Replace "Sheet1" with your actual tab name if different

# 4. Read a value to test the connection
value = worksheet.acell('A1').value
print(f"Current value in A1: {value}")

# 5. Write a new value to a specific cell
worksheet.update_acell('B1', 'Edited by Python!')
print("Successfully updated cell B1.")