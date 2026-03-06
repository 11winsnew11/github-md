import os
import datetime
import subprocess

# CONFIGURATION
# ----------------
TARGET_YEAR = 2026 
CLEAN_PREVIOUS_COMMITS = True 

TEXT = [
    "1   1   1  1   1  111  1   1  11111  1   1",
    "1   1   1  11  1  1    11  1  1      1   1",
    "1 1 1   1  1 1 1  111  1 1 1  111    1 1 1",
    "1 1 1   1  1  11    1  1  11  1      1 1 1",
    "1   1   1  1   1  111  1   1  11111  1   1"
]

def create_commit(date):
    git_date = date.strftime("%Y-%m-%d %H:%M")
    # Pesan commit "WINSNEW" digunakan sebagai penanda untuk dibersihkan nantinya
    command = f'GIT_AUTHOR_DATE="{git_date}" GIT_COMMITTER_DATE="{git_date}" git commit --allow-empty -m "WINSNEW"'
    os.system(command)

def clean_previous_drawing():
    """
    Fungsi ini menghapus commit HANYA jika pesannya adalah "WINSNEW".
    Ini lebih aman karena tidak menghapus commit kode asli Anda yang mungkin ada di tahun yang sama.
    """
    print(f"!!! ACTION: Cleaning previous drawing ('WINSNEW') !!!")
    
    # Perintah filter-branch untuk menyaring commit berdasarkan pesan
    # Logika: Jika pesan commit adalah "WINSNEW", lewati (hapus). Jika tidak, pertahankan.
    filter_cmd = (
        'git filter-branch --force --commit-filter '
        '\'if [ "$GIT_COMMIT" = "$(git rev-parse HEAD)" ] && [ "$(git log -1 --format=%s $GIT_COMMIT)" = "WINSNEW" ]; then '
        'skip_commit "$@"; '
        'elif [ "$(git log -1 --format=%s $GIT_COMMIT)" = "WINSNEW" ]; then '
        'skip_commit "$@"; '
        'else git commit-tree "$@"; fi\' HEAD'
    )
    
    # Alternatif perintah yang lebih sederhana dan kompatibel (Linux/Mac/Windows Git Bash):
    # Hapus semua commit yang pesannya mengandung "WINSNEW"
    simple_filter_cmd = (
        'git filter-branch --force --commit-filter '
        '\'if [ "$(git log -1 --format=%s $GIT_COMMIT)" = "WINSNEW" ]; then '
        'skip_commit "$@"; else git commit-tree "$@"; fi\' HEAD'
    )

    os.system(simple_filter_cmd)
    
    # Bersihkan jejak reflog dan references agar commit benar-benar hilang
    os.system("rm -rf .git/refs/original/")
    os.system("git reflog expire --expire=now --all")
    os.system("git gc --prune=now --aggressive")
    print("Clean up complete. The grid is now clear for new drawing.")

# --- DATE LOGIC ---
target_date = datetime.date(TARGET_YEAR, 1, 1)
days_to_subtract = (target_date.weekday() + 1) % 7
start_date = target_date - datetime.timedelta(days=days_to_subtract)

weeks_in_year = datetime.date(TARGET_YEAR, 12, 28).isocalendar()[1]
text_width = max(len(row) for row in TEXT)
week_offset = (weeks_in_year - text_width) // 2
day_offset = 1 

print(f"Target Year: {TARGET_YEAR}")
print(f"Start Date (Sunday): {start_date}")

# --- CLEAN UP PROCESS ---
if CLEAN_PREVIOUS_COMMITS:
    print("Checking for previous drawing commits to delete...")
    # Cek apakah ada commit dengan pesan "WINSNEW"
    check_log = subprocess.getoutput('git log --oneline --grep="WINSNEW"')
    
    if check_log:
        print(f"Found previous drawing commits. Cleaning...")
        clean_previous_drawing()
    else:
        print("No previous drawing found. Canvas is clean.")

# --- DRAWING PROCESS ---
print(f"Centering Image: Week offset {week_offset}, Day offset {day_offset}")
padded_text = [row.ljust(text_width) for row in TEXT]
print("Starting drawing WINSNEW (Centered & Neat)...")

for col in range(text_width):
    for row in range(len(padded_text)):
        if padded_text[row][col] == '1':
            current_date = start_date + datetime.timedelta(weeks=col + week_offset, days=row + day_offset)
            
            print(f"Committing for: {current_date}")
            create_commit(current_date)

print("Drawing complete! Pushing to GitHub...")
os.system("git push -f origin main")