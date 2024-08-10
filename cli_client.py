import requests
import json
import threading
import time

from server import run_server

BASE_URL = "http://127.0.0.1:8000"

def add_expense():
    name = input("Enter expense name: ")
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    currency = input("Enter currency: ")
    tag = input("Enter tag: ")
    notes = input("Enter notes: ")

    expense = {
        "name": name,
        "category": category,
        "amount": amount,
        "currency": currency,
        "tag": tag,
        "notes": notes
    }

    response = requests.post(f"{BASE_URL}/expenses/", json=expense)
    if response.status_code == 201:
        print("Expense added successfully:", response.json())
    else:
        print("Failed to add expense:", response.status_code, response.text)

def get_expenses():
    tag = input("Filter by tag (leave blank for no filter): ")
    category = input("Filter by category (leave blank for no filter): ")
    currency = input("Filter by currency (leave blank for no filter): ")

    params = {}
    if tag:
        params['tag'] = tag
    if category:
        params['category'] = category
    if currency:
        params['currency'] = currency

    response = requests.get(f"{BASE_URL}/expenses/", params=params)
    if response.status_code == 200:
        expenses = response.json()
        print("Expenses retrieved successfully:")
        for expense in expenses:
            print(json.dumps(expense, indent=4))
    else:
        print("Failed to retrieve expenses:", response.status_code, response.text)

def update_expense():
    expense_id = input("Enter the ID of the expense to update: ")
    name = input("Enter new expense name: ")
    category = input("Enter new category: ")

    amount = float(input("Enter new amount: "))
    currency = input("Enter new currency: ")
    tag = input("Enter new tag: ")
    notes = input("Enter new notes: ")

    updated_expense = {
        "name": name,
        "category": category,
        "amount": amount,
        "currency": currency,
        "tag": tag,
        "notes": notes
    }

    response = requests.put(f"{BASE_URL}/expenses/{expense_id}", json=updated_expense)
    if response.status_code == 200:
        print("Expense updated successfully:", response.json())
    else:
        print("Failed to update expense:", response.status_code, response.text)

def delete_expense():
    expense_id = input("Enter the ID of the expense to delete: ")

    response = requests.delete(f"{BASE_URL}/expenses/{expense_id}")
    if response.status_code == 200:
        print("Expense deleted successfully")
    else:
        print("Failed to delete expense:", response.status_code, response.text)

def main():
    while True:
        print("\nExpense Tracker CMD Client")
        print("1. Add Expense")
        print("2. Get Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            get_expenses()
        elif choice == '3':
            update_expense()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

if __name__ == "__main__":
    start_server()
    # Wait for the server to start :-)
    time.sleep(0.5)
    main()
