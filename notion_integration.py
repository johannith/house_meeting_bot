from constants import NOTION_TOKEN, HOUSE_MEETING_DATABASE_ID, HOUSE_PROJECTS_DATABASE_ID, TEMPLATE_MEETING_PAGE_ID
from notion_client import Client
from constants import HOUSE_MEETING_LINK, HOUSE_PROJECTS_LINK, OWNERS
import os
from datetime import datetime, timedelta
from house_meeting_template import get_house_meeting_template_blocks
from ynab_integration import get_ynab_house_spending_table, get_ynab_house_transactions_for_prev_month

notion = Client(auth=NOTION_TOKEN)

def get_first_tuesday(year, month):
    d = datetime(year, month, 1)
    while d.weekday() != 1:
        d += timedelta(days=1)
    return d

def should_send_email():
    today = datetime.now().date()
    first_tuesday = get_first_tuesday(today.year, today.month).date()
    days_before = (first_tuesday - today).days
    return days_before in [14, 7, 2, 0]

def fetch_most_recent_meeting():
    today = datetime.now().date()
    response = notion.databases.query(
        database_id=HOUSE_MEETING_DATABASE_ID,
        sorts=[{"property": "Meeting Date", "direction": "descending"}],
        page_size=10
    )
    results = response.get('results', [])
    for meeting in results:
        props = meeting["properties"]
        meeting_date_prop = props.get("Meeting Date", {})
        meeting_date = meeting_date_prop.get("date", {}).get("start")
        if meeting_date:
            meeting_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()
            if meeting_date <= today:
                return meeting
    return None

def fetch_tasks_from_meeting(meeting_page):
    tasks = []
    properties = meeting_page["properties"]
    house_tasks = properties["House Projects"]["relation"]
    for house_task in house_tasks:
        task_id = house_task["id"]
        task = fetch_task_by_id(task_id)
        if task:
            tasks.append(task)
    return tasks

def fetch_task_by_id(task_id):
    page = notion.pages.retrieve(page_id=task_id)
    props = page["properties"]
    name = props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "Untitled"
    status = props["Status"]["status"]["name"] if props["Status"]["status"] else "Unknown"
    if "Owner" in props and "multi_select" in props["Owner"]:
        owners = props["Owner"]["multi_select"]
        owner = ", ".join([o["name"] for o in owners]) if owners else "Unassigned"
    else:
        owner = "Unassigned"
    assigned_date = props["Date Assigned"]["date"].get("start")
    return {"name": name, "status": status, "owner": owner, "assigned_date": assigned_date}

def format_task_line(task):
    assigned_str = f" (assigned {task['assigned_date'][:10]})" if task.get('assigned_date') else ""
    if task["status"].lower() == "done":
        return f"✅ {task['name']}{assigned_str} – 🎉 Yay! You've completed {task['name']}. Amazing work!"
    else:
        return f"❌ {task['name']}{assigned_str} – {task['name']} is still on the to-do list—let's tackle it together! 🙌"

def group_tasks_by_owner(tasks):
    grouped = {"Johanni": [], "Jimmy": [], "Other": []}
    for task in tasks:
        owner = task["owner"]
        formatted = format_task_line(task)
        task_with_format = dict(task)
        task_with_format['formatted'] = formatted
        found = False
        for key, names in OWNERS.items():
            if owner in names:
                grouped[key].append(task_with_format)
                found = True
                break
        if not found:
            grouped["Other"].append(task_with_format)
    return grouped

def get_next_meeting_page():
    next_meeting_date = get_next_first_tuesday()
    response = notion.databases.query(
        database_id=HOUSE_MEETING_DATABASE_ID,
        filter={
            "property": "Meeting Date",
            "date": {"equals": next_meeting_date.strftime("%Y-%m-%d")}
        }
    )
    results = response.get('results', [])
    if results:
        return results[0]
    return None

def get_next_first_tuesday():
    today = datetime.now().date()
    year, month = today.year, today.month
    first_tuesday = get_first_tuesday(year, month).date()
    if today > first_tuesday:
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        first_tuesday = get_first_tuesday(year, month).date()
    return first_tuesday

def meeting_exists_for_date(date_to_check):
    response = notion.databases.query(
        database_id=HOUSE_MEETING_DATABASE_ID,
        filter={
            "property": "Meeting Date",
            "date": {"equals": date_to_check.strftime("%Y-%m-%d")}
        }
    )
    results = response.get('results', [])
    return len(results) > 0

def needs_new_meeting_entry():
    next_meeting_date = get_next_first_tuesday()
    if meeting_exists_for_date(next_meeting_date):
        return False, next_meeting_date
    return True, next_meeting_date

def get_next_meeting_number():
    response = notion.databases.query(
        database_id=HOUSE_MEETING_DATABASE_ID,
        page_size=100
    )
    max_num = 0
    for page in response.get('results', []):
        props = page.get('properties', {})
        name_title = props.get('Name', {}).get('title', [])
        if name_title:
            name_text = name_title[0].get('plain_text', '')
            if name_text.startswith('#'):
                try:
                    num = int(name_text[1:].split()[0])
                    if num > max_num:
                        max_num = num
                except Exception:
                    continue
    return max_num + 1

def create_meeting_from_template(meeting_date):
    meeting_number = get_next_meeting_number()
    title = f"#{meeting_number}"
    properties = {
        "Name": {
            "title": [
                {"type": "text", "text": {"content": title}}
            ]
        },
        "Meeting Date": {
            "date": {"start": meeting_date.strftime("%Y-%m-%d")}
        }
    }
    children = get_house_meeting_template_blocks()
    new_page = notion.pages.create(
        parent={"database_id": HOUSE_MEETING_DATABASE_ID},
        properties=properties,
        children=children
    )
    print(f"Created new House Meeting entry for {meeting_date}")
    return new_page

def fetch_all_not_started_tasks():
    tasks = []
    response = notion.databases.query(
        database_id=HOUSE_PROJECTS_DATABASE_ID,
        filter={
            "property": "Status",
            "status": {"equals": "Not Started"}
        },
        page_size=100
    )
    for page in response.get('results', []):
        task = fetch_task_by_id(page['id'])
        if task:
            tasks.append(task)
    return tasks

def update_ynab_section_in_next_meeting():
    """
    Updates the YNAB section in the upcoming house meeting page with a Notion table block of house spending by month and total, and a second table of individual house transactions for the previous month.
    """
    next_meeting_page = get_next_meeting_page()
    if not next_meeting_page:
        print("No upcoming meeting page found.")
        return
    page_id = next_meeting_page['id']
    # Get all blocks in the page
    blocks = notion.blocks.children.list(page_id).get('results', [])
    # Find the YNAB callout block
    ynab_callout_idx = None
    for i, block in enumerate(blocks):
        if block['type'] == 'callout' and 'YNAB' in blocks[i-1].get('heading_1', {}).get('rich_text', [{}])[0].get('text', {}).get('content', ''):
            ynab_callout_idx = i
            break
    if ynab_callout_idx is None:
        print("YNAB callout block not found.")
        return
    # Remove any table blocks immediately after the callout (until next heading or callout)
    to_delete = []
    for j in range(ynab_callout_idx+1, len(blocks)):
        block_type = blocks[j]['type']
        if block_type in ('heading_1', 'callout'):
            break
        if block_type == 'table':
            to_delete.append(blocks[j]['id'])
    for block_id in to_delete:
        notion.blocks.delete(block_id)
    # Prepare the summary table block
    spending_table = get_ynab_house_spending_table()
    if not spending_table:
        print("No house spending data found.")
        return
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # Calculate monthly totals across all categories
    monthly_totals = {m: 0.0 for m in range(1, 13)}
    grand_total = 0.0
    for months in spending_table.values():
        for m in range(1, 13):
            monthly_totals[m] += months.get(m, 0.0)
        grand_total += months.get('total', 0.0)
    table_block = {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 14,
            "has_column_header": True,
            "has_row_header": False,
            "children": [
                {
                    "object": "block",
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Spending Category"}}]
                        ] + [
                            [{"type": "text", "text": {"content": m}}] for m in month_names
                        ] + [
                            [{"type": "text", "text": {"content": "Total"}}]
                        ]
                    }
                },
            ] + [
                {
                    "object": "block",
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": cat}}]
                        ] + [
                            [
                                {"type": "text", "text": {"content": f"${months[m]:,.2f}" if months[m] else ""}}
                            ] for m in range(1, 13)
                        ] + [
                            [{"type": "text", "text": {"content": f"${months['total']:,.2f}"}}]
                        ]
                    }
                } for cat, months in spending_table.items()
            ] + [
                {
                    "object": "block",
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Total (All Categories)"}}]
                        ] + [
                            [
                                {"type": "text", "text": {"content": f"${monthly_totals[m]:,.2f}" if monthly_totals[m] else ""}}
                            ] for m in range(1, 13)
                        ] + [
                            [{"type": "text", "text": {"content": f"${grand_total:,.2f}"}}]
                        ]
                    }
                }
            ]
        }
    }
    # Prepare the transactions table block for previous month
    from datetime import datetime
    meeting_date_str = next_meeting_page['properties'].get('Meeting Date', {}).get('date', {}).get('start')
    tx_table_block = None
    if meeting_date_str:
        meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d").date()
        transactions = get_ynab_house_transactions_for_prev_month(meeting_date)
        if transactions:
            tx_table_block = {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 5,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": "Date"}}],
                                    [{"type": "text", "text": {"content": "Payee"}}],
                                    [{"type": "text", "text": {"content": "Category"}}],
                                    [{"type": "text", "text": {"content": "Memo"}}],
                                    [{"type": "text", "text": {"content": "Outflow"}}]
                                ]
                            }
                        },
                    ] + [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"type": "text", "text": {"content": row[0]}}],
                                    [{"type": "text", "text": {"content": row[1]}}],
                                    [{"type": "text", "text": {"content": row[2]}}],
                                    [{"type": "text", "text": {"content": row[3]}}],
                                    [{"type": "text", "text": {"content": row[4]}}]
                                ]
                            }
                        } for row in transactions
                    ]
                }
            }
    # Insert the tables as siblings after the callout block (not as children)
    # Use the Notion API to append after the callout block
    after_block_id = blocks[ynab_callout_idx]['id']
    children_to_add = [table_block]
    if tx_table_block:
        children_to_add.append(tx_table_block)
    notion.blocks.children.append(
        page_id,
        children=children_to_add,
        after=after_block_id
    )
    print("YNAB section updated with house spending tables.")
    return 