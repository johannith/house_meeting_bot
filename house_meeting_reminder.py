from notion_integration import (
    should_send_email, needs_new_meeting_entry, create_meeting_from_template,
    update_ynab_section_in_next_meeting, fetch_most_recent_meeting,
    get_next_meeting_page, fetch_all_not_started_tasks, group_tasks_by_owner
)
from email_utils import build_email_body, send_email


def main():
    need_new, next_meeting_date = needs_new_meeting_entry()
    if need_new:
        create_meeting_from_template(next_meeting_date)
        print("New meeting entry created. Please fill in any additional details in Notion.")
    # Always update the YNAB section for the next meeting
    update_ynab_section_in_next_meeting()
    meeting = fetch_most_recent_meeting()
    if not meeting:
        print("No recent meeting found.")
        return
    # Get the next meeting page and its URL
    next_meeting_page = get_next_meeting_page()
    next_meeting_url = None
    if next_meeting_page:
        next_meeting_url = next_meeting_page.get('url')
    tasks = fetch_all_not_started_tasks()
    grouped = group_tasks_by_owner(tasks)
    
    if not should_send_email():
        print("Not sending email.")
        return
    
    body = build_email_body(grouped, next_meeting_url=next_meeting_url)
    subject = "🏡 House Meeting Prep – Let's Check In and Celebrate Progress!"
    send_email(subject, body)
    print("Email sent!")

if __name__ == "__main__":
    main() 