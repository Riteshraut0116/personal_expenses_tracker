import csv
import os
from datetime import datetime
from collections import defaultdict

FILE_NAME = 'expenses.csv'
HEADERS = ['Date', 'Category', 'Description', 'Amount']

def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(HEADERS)

def get_expenses():
    """Reads all expenses from the CSV file and returns them as a list of lists."""
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader) # Skip header
        return list(reader)

def save_all_expenses(expenses):
    """Saves a list of expenses to the CSV file, overwriting existing content."""
    with open(FILE_NAME, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADERS)
        writer.writerows(expenses)

def add_expense():
    """Prompts the user for expense details and saves them to the CSV file."""
    date_str = input(f"Enter the date (YYYY-MM-DD), or press Enter for today ({datetime.now().strftime('%Y-%m-%d')}): ")
    if not date_str:
        date = datetime.now().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            date = date_str
        except ValueError:
            print("Invalid date format. Using today's date.")
            date = datetime.now().strftime('%Y-%m-%d')

    category = input("Enter the category (e.g., Food, Transport, Bills): ")
    description = input("Enter a brief description: ")

    while True:
        try:
            amount = float(input("Enter the amount: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value for the amount.")

    with open(FILE_NAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([date, category, description, f"{amount:.2f}"])

    print("\n✅ Expense added successfully!")

def view_expenses(show_index=False):
    """Reads and displays all expenses from the CSV file."""
    expenses = get_expenses()

    if not expenses:
        print("\nNo expenses recorded yet. Start by adding one!")
        return False

    print("\n--- All Expenses ---")
    header_format = f"{'No.':<5} | {HEADERS[0]:<12} | {HEADERS[1]:<15} | {HEADERS[2]:<30} | {HEADERS[3]:>10}" if show_index else f"{HEADERS[0]:<12} | {HEADERS[1]:<15} | {HEADERS[2]:<30} | {HEADERS[3]:>10}"
    print(header_format)
    print("-" * 80)

    total_amount = 0.0
    for i, row in enumerate(expenses):
        total_amount += float(row[3])
        if show_index:
            print(f"{i+1:<5} | {row[0]:<12} | {row[1]:<15} | {row[2]:<30} | {row[3]:>10}")
        else:
            print(f"{row[0]:<12} | {row[1]:<15} | {row[2]:<30} | {row[3]:>10}")

    print("-" * 80)
    print(f"{'Total:':<65} {total_amount:>10.2f}")
    return True

def edit_expense():
    """Allows the user to edit an existing expense."""
    expenses = get_expenses()
    if not view_expenses(show_index=True):
        return

    try:
        choice = int(input("\nEnter the number of the expense to edit: "))
        if not 1 <= choice <= len(expenses):
            print("Invalid number. Please try again.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    expense_index = choice - 1
    expense = expenses[expense_index]

    print("\nEditing expense. Press Enter to keep the current value.")

    # Edit Date
    new_date_str = input(f"Date ({expense[0]}): ")
    if new_date_str:
        try:
            datetime.strptime(new_date_str, '%Y-%m-%d')
            expense[0] = new_date_str
        except ValueError:
            print("Invalid date format. Keeping original date.")

    # Edit Category
    new_category = input(f"Category ({expense[1]}): ")
    if new_category:
        expense[1] = new_category

    # Edit Description
    new_description = input(f"Description ({expense[2]}): ")
    if new_description:
        expense[2] = new_description

    # Edit Amount
    while True:
        new_amount_str = input(f"Amount ({expense[3]}): ")
        if not new_amount_str:
            break # Keep original
        try:
            expense[3] = f"{float(new_amount_str):.2f}"
            break
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")

    expenses[expense_index] = expense
    save_all_expenses(expenses)
    print("\n✅ Expense updated successfully!")

def filter_expenses():
    """Filters expenses by category, year, and/or month and displays them."""
    expenses = get_expenses()
    if not expenses:
        print("\nNo expenses recorded yet. Start by adding one!")
        return

    # Get unique categories for user convenience
    categories = sorted(list(set(row[1] for row in expenses)))
    print("\nAvailable categories:", ", ".join(categories))
    filter_category = input("Enter category to filter by (or press Enter for all): ").strip().lower()
    filter_year = input("Enter year to filter by (e.g., 2023) (or press Enter for all): ").strip()
    filter_month = input("Enter month to filter by (1-12) (or press Enter for all): ").strip()

    filtered_list = []
    for expense in expenses:
        try:
            expense_date = datetime.strptime(expense[0], '%Y-%m-%d')
        except (ValueError, IndexError):
            continue  # Skip malformed rows

        # Match criteria (empty filter means match all)
        category_match = not filter_category or expense[1].lower() == filter_category
        year_match = not filter_year or str(expense_date.year) == filter_year
        month_match = not filter_month or str(expense_date.month) == filter_month

        if category_match and year_match and month_match:
            filtered_list.append(expense)

    if not filtered_list:
        print("\nNo expenses found matching your criteria.")
        return

    print("\n--- Filtered Expenses ---")
    header_format = f"{HEADERS[0]:<12} | {HEADERS[1]:<15} | {HEADERS[2]:<30} | {HEADERS[3]:>10}"
    print(header_format)
    print("-" * 80)

    total_amount = 0.0
    for row in filtered_list:
        total_amount += float(row[3])
        print(f"{row[0]:<12} | {row[1]:<15} | {row[2]:<30} | {row[3]:>10}")

    print("-" * 80)
    print(f"{'Filtered Total:':<65} {total_amount:>10.2f}")

def view_summary():
    """Displays a summary of expenses by month and year."""
    expenses = get_expenses()
    if not expenses:
        print("\nNo expenses to summarize.")
        return

    summary = defaultdict(lambda: defaultdict(float))
    grand_total = 0.0

    for date_str, _, _, amount_str in expenses:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            amount = float(amount_str)
            summary[date.year][date.strftime('%B')] += amount
            grand_total += amount
        except (ValueError, IndexError):
            print(f"Skipping malformed row: {[date_str, _, _, amount_str]}")
            continue

    print("\n--- Expense Summary ---")
    for year in sorted(summary.keys()):
        print(f"\n--- {year} ---")
        year_total = 0.0
        for month in sorted(summary[year].keys(), key=lambda m: datetime.strptime(m, "%B").month):
            month_total = summary[year][month]
            year_total += month_total
            print(f"  {month:<10}: {month_total:10.2f}")
        print("-" * 25)
        print(f"  {'Year Total':<10}: {year_total:10.2f}")

    print("\n" + "=" * 25)
    print(f"{'Grand Total':<12}: {grand_total:10.2f}")
    print("=" * 25)

def main():
    """Main function to run the expense tracker application."""
    initialize_csv()
    while True:
        print("\n======= Personal Expense Tracker =======")
        print("1. Add a new expense")
        print("2. View all expenses")
        print("3. Edit an expense")
        print("4. Filter expenses")
        print("5. View expense summary (by month/year)")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            edit_expense()
        elif choice == '4':
            filter_expenses()
        elif choice == '5':
            view_summary()
        elif choice == '6':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()