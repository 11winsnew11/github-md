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
    git_date = date.strftime("%Y-%m-%d %H:%M")
    command = f'GIT_AUTHOR_DATE="{git_date}" GIT_COMMITTER_DATE="{git_date}" git commit --allow-empty -m "WINSNEW"'
    os.system(command)

def clean_previous_drawing():
    """
    Menghapus commit 'WINSNEW' menggunakan file skrip eksternal untuk menghindari error parsing shell.
    """
    print(f"!!! ACTION: Cleaning previous drawing ('WINSNEW') !!!")
    
    # 1. Ambil daftar hash commit yang ingin dihapus
    try:
        # Filter hanya commit di tahun target dan pesan WINSNEW untuk efisiensi
        cmd = f'git log --grep="WINSNEW" --after="{TARGET_YEAR}-01-01" --before="{TARGET_YEAR+1}-01-01" --format=%H'
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        
        if not output:
            print("No drawing commits found to clean.")
            return
        
        hashes = output.split('\n')
        print(f"Found {len(hashes)} drawing commits to remove.")
    except subprocess.CalledProcessError:
        print("No drawing commits found.")
        return

    # 2. Buat file skrip sementara untuk filter-branch
    # Ini jauh lebih stabil daripada menulis logic if/else di dalam string os.system
    script_content = "#!/bin/sh\n\n"
    
    # Logika: Jika hash cocok, jangan print apapun (drop commit). Jika tidak, cetak hash baru.
    # Karena filter-branch memproses satu per satu, kita cek apakah GIT_COMMIT ada di daftar kita.
    # Namun membandingkan string di sh lebih mudah.
    
    # Kita buat kondisi pengecekan
    check_list = " ".join(hashes)
    script_content += f'''
    TARGET_COMMITS="{check_list}"
    
    # Cek apakah commit saat ini ada di daftar target
    case " $TARGET_COMMITS " in
      *" $GIT_COMMIT "*)
        # Commit ini adalah WINSNEW, skip (jangan print hash baru)
        # Untuk skip di commit-filter, kita cukup tidak mengeluarkan output
        ;;
      *)
        # Commit lain, pertahankan
        git commit-tree "$@"
        ;;
    esac
    '''
    
    script_filename = "_clean_filter_script.sh"
    with open(script_filename, "w") as f:
        f.write(script_content)
    
    # 3. Jalankan filter-branch menggunakan file tsb
    # Kita pakai 'sh' agar kompatibel Windows (via Git Bash) dan Linux
    filter_cmd = f'git filter-branch --force --commit-filter "sh {script_filename}" HEAD'
    
    print("Running cleanup script...")
    exit_code = os.system(filter_cmd)
    
    # 4. Bersih-bersih
    if os.path.exists(script_filename):
        os.remove(script_filename)
        
    if exit_code != 0:
        print("WARNING: Filter branch failed. Attempting full year reset as fallback...")
        # Fallback: Hapus seluruh tahun jika filter gagal (misal permission issue)
        clean_year_fallback(TARGET_YEAR)
    else:
        # Standar cleanup setelah filter-branch
        os.system("rm -rf .git/refs/original/")
        os.system("git reflog expire --expire=now --all")
        os.system("git gc --prune=now --aggressive")
        print("Cleanup complete.")

def clean_year_fallback(year):
    """Metode lama: menghapus seluruh commit di tahun tersebut."""
    print(f"Running fallback cleaner for year {year}...")
    filter_cmd = f'git filter-branch --force --commit-filter \'if [ "$(echo "$GIT_AUTHOR_DATE" | grep -c "{year}")" -gt 0 ]; then skip_commit "$@"; else git commit-tree "$@"; fi\' HEAD'
    os.system(filter_cmd)
    os.system("rm -rf .git/refs/original/")
    os.system("git reflog expire --expire=now --all")
    os.system("git gc --prune=now --aggressive")

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