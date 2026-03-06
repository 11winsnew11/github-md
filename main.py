import os
import datetime

# CONFIGURATION
# ----------------
WEEKS_OFFSET = 0 

TEXT = [
    "1   1    1    1   1   111   1   1   111   1   1",
    "1   1    1    11  1   1     11  1   1     1   1",
    "1 1 1    1    1 1 1   11    1 1 1   111   1 1 1",
    "1 1 1    1    1  11     1   1  11   1     1 1 1",
    "1   1    1    1   1   111   1   1   111   1   1",
    "                                           ",
    "                                           "
]

def create_commit(date):
    git_date = date.strftime("%Y-%m-%d %H:%M")
    command = f'GIT_AUTHOR_DATE="{git_date}" GIT_COMMITTER_DATE="{git_date}" git commit --allow-empty -m "WINSNEW"'
    os.system(command)

today = datetime.date.today()
start_date = today - datetime.timedelta(weeks=52+WEEKS_OFFSET, days=today.weekday()+1)

print("Starting drawing WINSNEW...")

width = len(TEXT[0])

for col in range(width):
    for row in range(7):
        if row < len(TEXT):
            if TEXT[row][col] == '1':
                current_date = start_date + datetime.timedelta(weeks=col, days=row)
                print(f"Committing for: {current_date}")
                create_commit(current_date)

print("Drawing complete! Pushing to GitHub...")
os.system("git push origin main") 