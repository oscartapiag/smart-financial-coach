import csv
import random
from datetime import datetime, timedelta

# Parameters
num_rows = 1000
start_date = datetime.today() - timedelta(days=180)  # ~6 months ago
categories = ["Groceries", "Restaurants", "Rent", "Utilities", "Entertainment",
              "Transportation", "Shopping", "Healthcare", "Salary", "Misc"]
merchants = {
    "Groceries": ["Safeway", "Trader Joe's", "Whole Foods", "Walmart"],
    "Restaurants": ["Chipotle", "McDonald's", "Olive Garden", "Subway"],
    "Rent": ["Landlord LLC"],
    "Utilities": ["PG&E", "AT&T", "Comcast"],
    "Entertainment": ["Netflix", "Spotify", "Hulu"],
    "Transportation": ["Uber", "Lyft", "Shell Gas", "Exxon"],
    "Shopping": ["Amazon", "Target", "Best Buy"],
    "Healthcare": ["CVS Pharmacy", "Walgreens"],
    "Salary": ["Company Payroll"],
    "Misc": ["Venmo", "PayPal"],
}

with open("sample_transaction_2.csv", "w", newline="") as csvfile:
    fieldnames = ["date", "description", "category", "amount", "account"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for _ in range(num_rows):
        days_offset = random.randint(0, 180)
        date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        category = random.choice(categories)
        merchant = random.choice(merchants[category])

        # Income vs expenses
        if category == "Salary":
            amount = round(random.uniform(2000, 4000), 2)  # big positive
        else:
            amount = -round(random.uniform(5, 200), 2)  # expenses negative

        writer.writerow({
            "date": date,
            "description": merchant,
            "category": category,
            "amount": amount,
            "account": "Checking"
        })

print("✅ Generated sample_transactions.csv with", num_rows, "rows")
