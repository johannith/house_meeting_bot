from constants import YNAB_API_KEY
import ynab
from collections import defaultdict

def get_ynab_house_spending_table():
    """
    Returns a dict: {category: {month: amount, ..., 'total': total_amount}} for all categories with 🏠 in the name
    in the 'Year of Bloom (2025)' budget, for all transactions in the current year.
    """
    configuration = ynab.Configuration(access_token=YNAB_API_KEY)
    with ynab.ApiClient(configuration) as api_client:
        budgets_api = ynab.BudgetsApi(api_client)
        budgets_response = budgets_api.get_budgets()
        budgets = budgets_response.data.budgets
        # Find the correct budget
        budget = next((b for b in budgets if b.name == "Year of Bloom (2025)"), None)
        if not budget:
            return {}
        budget_id = budget.id
        # Get all categories
        categories_api = ynab.CategoriesApi(api_client)
        categories_response = categories_api.get_categories(budget_id)
        categories = categories_response.data.category_groups
        # Map category_id to name (with emoji)
        cat_id_to_name = {}
        for group in categories:
            for cat in group.categories:
                cat_id_to_name[cat.id] = cat.name
        # Get all transactions for this year
        from datetime import date
        year = date.today().year
        year_start = date(year, 1, 1)
        transactions_api = ynab.TransactionsApi(api_client)
        transactions_response = transactions_api.get_transactions(budget_id, since_date=year_start)
        transactions = transactions_response.data.transactions
        # Sum spending by category and month (only 🏠)
        spending = defaultdict(lambda: defaultdict(float))
        for txn in transactions:
            cat_name = cat_id_to_name.get(txn.category_id, "")
            if "🏠" in cat_name and txn.amount < 0:  # Only outflows
                txn_date = getattr(txn, 'var_date', None)
                if txn_date is None:
                    print('ERROR: Transaction missing date:', txn, "!!!!")
                    continue
                spending[cat_name][txn_date.month] += abs(txn.amount) / 1000  # YNAB uses milliunits
        # Add total per category
        result = {}
        for cat, months in spending.items():
            total = sum(months[m] for m in range(1, 13))
            result[cat] = {m: months.get(m, 0.0) for m in range(1, 13)}
            result[cat]['total'] = total
        return result

def get_ynab_house_transactions_for_prev_month(meeting_date):
    """
    Returns a list of (date, payee, category, memo, outflow) for all 🏠 outflow transactions in the previous month of the given meeting_date.
    """
    from datetime import date, timedelta
    configuration = ynab.Configuration(access_token=YNAB_API_KEY)
    with ynab.ApiClient(configuration) as api_client:
        budgets_api = ynab.BudgetsApi(api_client)
        budgets_response = budgets_api.get_budgets()
        budgets = budgets_response.data.budgets
        budget = next((b for b in budgets if b.name == "Year of Bloom (2025)"), None)
        if not budget:
            return []
        budget_id = budget.id
        # Get all categories
        categories_api = ynab.CategoriesApi(api_client)
        categories_response = categories_api.get_categories(budget_id)
        categories = categories_response.data.category_groups
        cat_id_to_name = {}
        for group in categories:
            for cat in group.categories:
                cat_id_to_name[cat.id] = cat.name
        # Calculate previous month range
        year = meeting_date.year
        month = meeting_date.month
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year
        from calendar import monthrange
        start_date = date(prev_year, prev_month, 1)
        end_date = date(prev_year, prev_month, monthrange(prev_year, prev_month)[1])
        # Get all transactions for previous month
        transactions_api = ynab.TransactionsApi(api_client)
        transactions_response = transactions_api.get_transactions(budget_id, since_date=start_date)
        transactions = transactions_response.data.transactions
        # Filter for 🏠, outflow, and in the correct month
        result = []
        for txn in transactions:
            cat_name = cat_id_to_name.get(txn.category_id, "")
            if txn.amount < 0 and "🏠" in cat_name and start_date <= txn.var_date <= end_date:
                result.append((
                    txn.var_date.strftime("%Y-%m-%d"),
                    txn.payee_name or "",
                    cat_name,
                    txn.memo or "",
                    f"${abs(txn.amount)/1000:,.2f}"
                ))
        return result 