import os
import datetime

# CONFIGURATION
# ----------------
TARGET_YEAR = 2026  

TEXT = [
    "                                         ", 
    "1   1   1   1   1   111   1   1   11111   1   1", 
    "1   1   1   11  1   1   11  1   1       1   1", 
    "1 1 1   1   1 1 1    11   1 1 1   111   1 1 1", 
    "1 1 1   1   1  11     1   1  11   1     1 1 1", 
    "1   1   1   1   1   111   1   1   11111   1   1", 
    "                                         "  
]

def create_commit(date):
    git_date = date.strftime("%Y-%m-%d %H:%M")
    command = f'GIT_AUTHOR_DATE="{git_date}" GIT_COMMITTER_DATE="{git_date}" git commit --allow-empty -m "WINSNEW"'
    os.system(command)

# --- DATE LOGIC ---
target_date = datetime.date(TARGET_YEAR, 1, 1)
days_to_subtract = (target_date.weekday() + 1) % 7
start_date = target_date - datetime.timedelta(days=days_to_subtract)

print(f"Target Year: {TARGET_YEAR}")
print(f"Start Date (Sunday): {start_date}")

max_width = max(len(row) for row in TEXT)
padded_text = [row.ljust(max_width) for row in TEXT]
print("process")
for col in range(max_width):
    for row in range(7):
        if padded_text[row][col] == '1':
            current_date = start_date + datetime.timedelta(weeks=col, days=row)
            
            print(f"Committing for: {current_date}")
            create_commit(current_date)

print("Drawing complete! Pushing to GitHub...")
os.system("git push origin main")