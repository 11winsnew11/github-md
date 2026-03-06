import os
import datetime
import subprocess
import sys

# CONFIGURATION
# ----------------
TARGET_YEAR = 2026 
CLEAN_PREVIOUS_COMMITS = True 
REPO_BRANCH = "main"  # Sesuaikan jika branch Anda 'master' atau lainnya

TEXT = [
    "1   1   1  1   1  111  1   1  11111  1   1",
    "1   1   1  11  1  1    11  1  1      1   1",
    "1 1 1   1  1 1 1  111  1 1 1  111    1 1 1",
    "1 1 1   1  1  11    1  1  11  1      1 1 1",
    "1   1   1  1   1  111  1   1  11111  1   1"
]

def create_commit(date):
    # Menggunakan pesan "WINSNEW" sesuai permintaan
    git_date = date.strftime("%Y-%m-%d %H:%M")
    command = f'GIT_AUTHOR_DATE="{git_date}" GIT_COMMITTER_DATE="{git_date}" git commit --allow-empty -m "WINSNEW"'
    os.system(command)

def clean_previous_drawing():
    """
    Modifikasi: Menghapus SEMUA commit yang terjadi di TARGET_YEAR.
    Ini memastikan grafik benar-benar bersih (kosong) sebelum menggambar.
    Metode ini lebih andal daripada mencari pesan commit tertentu.
    """
    print(f"!!! ACTION: Cleaning ALL commits in year {TARGET_YEAR} !!!")
    
    # Membuat skrip shell sementara untuk filter-branch
    # Logika: Jika tanggal commit mengandung TARGET_YEAR, hapus (skip). Jika tidak, pertahankan.
    script_content = f"""#!/bin/sh
    
    # Ambil tanggal author
    COMMIT_DATE=$(git log -1 --format=%aI $GIT_COMMIT)
    
    # Cek apakah tahun ada di tanggal
    if echo "$COMMIT_DATE" | grep -q "{TARGET_YEAR}"; then
        # Tidak print apapun = menghapus commit
        exit 0
    else
        # Print hash baru = mempertahankan commit
        git commit-tree "$@"
    fi
    """
    
    script_filename = "_clean_filter_script.sh"
    with open(script_filename, "w") as f:
        f.write(script_content)
    
    # Jalankan filter-branch
    # Menambahkan -- --all untuk memastikan semua branch/riwayat bersih jika diperlukan,
    # namun HEAD biasanya cukup untuk branch saat ini.
    filter_cmd = f'git filter-branch --force --commit-filter "sh {script_filename}" HEAD'
    
    print("Running cleanup... (this may take a moment)")
    exit_code = os.system(filter_cmd)
    
    # Hapus file skrip sementara
    if os.path.exists(script_filename):
        os.remove(script_filename)
        
    if exit_code != 0:
        print("ERROR: Cleanup failed. Please check your git status or permissions.")
        sys.exit(1)
    else:
        # Standar cleanup git setelah filter-branch
        os.system("rm -rf .git/refs/original/")
        os.system("git reflog expire --expire=now --all")
        os.system("git gc --prune=now --aggressive")
        print(f"Year {TARGET_YEAR} cleaned successfully.")

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
    clean_previous_drawing()

# --- DRAWING PROCESS ---
print(f"Centering Image: Week offset {week_offset}, Day offset {day_offset}")
padded_text = [row.ljust(text_width) for row in TEXT]
print("Starting drawing WINSNEW...")

for col in range(text_width):
    for row in range(len(padded_text)):
        if padded_text[row][col] == '1':
            current_date = start_date + datetime.timedelta(weeks=col + week_offset, days=row + day_offset)
            
            print(f"Committing for: {current_date}")
            create_commit(current_date)

print("Drawing complete! Pushing to GitHub...")
os.system(f"git push -f origin {REPO_BRANCH}")