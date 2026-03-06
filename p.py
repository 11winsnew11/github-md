import subprocess
import sys
import os

def main():
    print("=== Skrip Perbaikan Tanggal Git & Hapus Commit Kosong ===")
    
    if not os.path.exists(".git"):
        print("Error: Jalankan skrip ini di dalam direktori repositori git.")
        return

    # --- CEK KONDISI FOLDER (DIRTY STATE) ---
    status_cmd = ["git", "status", "--porcelain"]
    status_result = subprocess.run(status_cmd, capture_output=True, text=True)
    
    if status_result.stdout.strip():
        print("\n[ ERROR ] Folder Anda tidak bersih!")
        print("Anda memiliki file yang telah diubah tapi belum di-commit.")
        print("Git melarang pengubahan history jika ada file yang belum disimpan.")
        print("\nSilakan jalankan perintah ini di terminal untuk menyimpan perubahan sementara:")
        print("  git stash")
        print("\nSetelah itu, jalankan skrip python ini lagi.")
        return
    # ---------------------------------------

    target_year = "2026"
    print(f"Mencari commit dengan tahun {target_year}...")
    
    try:
        new_year = int(input("Masukkan tahun pengganti (misal: 2024 atau 2025): "))
        if new_year == 2026:
            print("Tahun pengganti tidak boleh sama.")
            return
    except ValueError:
        print("Input tidak valid.")
        return

    # Ambil log
    cmd = ["git", "log", "--date=format:%Y", "--pretty=format:%H|%ad|%s"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    
    commits_2026 = [line for line in lines if f"|{target_year}|" in line]
    
    if not commits_2026:
        print(f"Tidak ada commit di tahun {target_year}.")
        return

    print(f"Ditemukan {len(commits_2026)} commit di tahun {target_year}.")
    print("\nPROSES YANG AKAN TERJADI:")
    print("1. Commit yang BERISI file -> Tanggal diubah ke tahun baru.")
    print("2. Commit yang KOSONG -> akan DIHAPUS.")
    print("Memulai proses rewrite history...")

    env = os.environ.copy()
    env['FILTER_BRANCH_SQUELCH_WARNING'] = '1'

    # Script filter untuk mengubah tanggal
    date_filter_script = f'''
    OLD_YEAR="{target_year}"
    NEW_YEAR="{new_year}"
    if [ "$(date -d "$GIT_AUTHOR_DATE" +%Y 2>/dev/null)" = "$OLD_YEAR" ]; then
        export GIT_AUTHOR_DATE=$(echo "$GIT_AUTHOR_DATE" | sed "s/$OLD_YEAR/$NEW_YEAR/g")
    fi
    if [ "$(date -d "$GIT_COMMITTER_DATE" +%Y 2>/dev/null)" = "$OLD_YEAR" ]; then
        export GIT_COMMITTER_DATE=$(echo "$GIT_COMMITTER_DATE" | sed "s/$OLD_YEAR/$NEW_YEAR/g")
    fi
    '''

    # Perintah utama: Menambahkan --prune-empty untuk menghapus commit yang kosong
    filter_cmd = [
        "git", "filter-branch", "-f", 
        "--env-filter", date_filter_script,
        "--prune-empty",  # <--- INI MODIFIKASI UTAMANYA
        "--", "--all"
    ]
    
    process = subprocess.Popen(filter_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("\n[ SUKSES ] Proses rewrite selesai.")
        print("Commit kosong di tahun 2026 telah dihapus.")
        print("Commit berisi di tahun 2026 telah dipindah tanggalnya.")
        print("\nSekarang jalankan perintah ini untuk update ke GitHub:")
        print("  git push --force --all")
    else:
        print("\n[ GAGAL ] Terjadi kesalahan:")
        print(stderr)

if __name__ == "__main__":
    main()