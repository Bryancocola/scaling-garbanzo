import os
import re
from datetime import datetime
from feedgen.feed import FeedGenerator

def parse_filename(filename):
    # Pattern: status (alert/post), then exactly 8 digits, then optional identifier
    # Example: alert09082025emergency.txt
    pattern = r"^(alert|post)(\d{8})\s*(.*)"
    match = re.match(pattern, filename, re.IGNORECASE)
    
    if not match:
        return None

    status = match.group(1).lower()
    date_str = match.group(2)
    identifier = match.group(3)
    
    try:
        # Parse mmddyyyy
        date_obj = datetime.strptime(date_str, "%m%d%Y")
    except ValueError:
        # Returns None if the 8 digits do not form a valid date (e.g., 13322025)
        return None

    return {
        'is_alert': status == 'alert',
        'date': date_obj,
        'identifier': identifier.strip(),
        'original_name': filename
    }

def generate_feed():
    fg = FeedGenerator()
    fg.id('http://github.com/your-repo/rss.xml')
    fg.title('Project Updates')
    fg.link(href='https://github.com/your-repo', rel='alternate')
    fg.description('RSS feed ordered by priority then date')

    entries = []
    # Scan current directory
    for filename in os.listdir('.'):
        if filename in ['generate_rss.py', 'rss.xml'] or os.path.isdir(filename):
            continue
            
        metadata = parse_filename(filename)
        if metadata:
            entries.append(metadata)

    # Sorting Logic:
    # 1. Alerts first (not True = 0, not False = 1)
    # 2. Date descending (newest at top)
    entries.sort(key=lambda x: (not x['is_alert'], x['date']), reverse=True)

    for entry in entries:
        fe = fg.add_entry()
        fe.id(entry['original_name'])
        
        prefix = "[ALERT]" if entry['is_alert'] else "[POST]"
        clean_date = entry['date'].strftime('%Y-%m-%d')
        fe.title(f"{prefix} {clean_date} {entry['identifier']}")
        
        # Replace USER/REPO with your actual GitHub details
        fe.link(href=f"https://github.com/USER/REPO/blob/main/{entry['original_name']}")
        fe.pubDate(entry['date'].astimezone())

    fg.rss_file('rss.xml')

if __name__ == "__main__":
    generate_feed()
