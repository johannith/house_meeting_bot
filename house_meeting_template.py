def get_house_meeting_template_blocks():
    """
    Returns a list of Notion API block objects representing the house meeting template.
    All checkboxes are unchecked, and callouts use a gray background with black text.
    """
    return [
        # House Meeting Agenda Heading
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "✨ House Meeting Agenda"}}]
            }
        },
        # Personal Calendar & Travel
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Personal Calendar & Travel"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Update personal calendars with upcoming trips & travel plans."}}]
            }
        },
        # Airbnb & Guest Schedule
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Airbnb & Guest Schedule"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Review who's available and which days to block."}}]
            }
        },
        # Couple's Workbook Time
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Couple's Workbook Time"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Schedule a dedicated time for joint planning and reflection."}}]
            }
        },
        # Cleaning & Upkeep
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Cleaning & Upkeep"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Any special cleaning requests?"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Discuss tasks that need to be done (but not by the cleaner)."}}]
            }
        },
        # Finances Check-In
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Finances Check-In"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Joint Account: Does it need more funds?"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Car Savings: Review or update."}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "House Spending: Just share, no guilt or judgment—let's align on lifestyle."}}]
            }
        },
        # Assign Monthly House Project
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Assign Monthly House Project"}, "annotations": {"bold": True}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Choose a shared project for the month—let's collaborate and enjoy the process."}}]
            }
        },
        # YNAB Heading
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "YNAB"}}]
            }
        },
        # YNAB Aside (callout) with gray background and black text
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "💡"},
                "rich_text": [{"type": "text", "text": {"content": "Joint household expenses for the past month"}}],
                "color": "gray_background"
            }
        },
        # New Talking Points Heading
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "✏️ New Talking Points"}}]
            }
        },
        # New Talking Points Aside (callout) with gray background and black text
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "🌟"},
                "rich_text": [{"type": "text", "text": {"content": "A dedicated space for each of us to add anything on our mind—big or small!\n\n- Ideas for the house\n- Financial questions\n- Upcoming events\n- Fun dreams and plans!"}}],
                "color": "gray_background"
            }
        },
        # Final empty list item
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "List"}}]
            }
        },
    ] 