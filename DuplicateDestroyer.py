import os
import hashlib
import fnmatch
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import platform
import datetime

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pencari File & Projek Duplikat")
        self.root.geometry("1100x650")
        
        self.dir_a = ""
        self.dir_b = ""
        
        # Variabel Opsi
        self.skip_hidden_var = tk.BooleanVar(value=True)
        self.skip_gitignore_var = tk.BooleanVar(value=True)
        
        self.create_widgets()

    def create_widgets(self):
        # --- Top Frame for Selection ---
        top_frame = tk.Frame(self.root, pady=10, padx=10)
        top_frame.pack(fill=tk.X)

        self.lbl_dir_a = tk.Label(top_frame, text="Lokasi A: Belum dipilih", fg="blue")
        self.lbl_dir_a.grid(row=0, column=0, sticky="w", padx=5)
        btn_dir_a = tk.Button(top_frame, text="Pilih Lokasi A", command=lambda: self.select_dir('A'))
        btn_dir_a.grid(row=0, column=1, padx=5)

        self.lbl_dir_b = tk.Label(top_frame, text="Lokasi B: Belum dipilih", fg="green")
        self.lbl_dir_b.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        btn_dir_b = tk.Button(top_frame, text="Pilih Lokasi B", command=lambda: self.select_dir('B'))
        btn_dir_b.grid(row=1, column=1, padx=5, pady=5)
        
        # --- Options Frame ---
        opt_frame = tk.Frame(top_frame)
        opt_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        chk_hidden = tk.Checkbutton(opt_frame, text="Skip folder/file tersembunyi (diawali titik)", variable=self.skip_hidden_var)
        chk_hidden.pack(side=tk.LEFT, padx=(0, 15))
        
        chk_gitignore = tk.Checkbutton(opt_frame, text="Skip folder/file yang ada di .gitignore", variable=self.skip_gitignore_var)
        chk_gitignore.pack(side=tk.LEFT)

        self.btn_scan = tk.Button(top_frame, text="Mulai Pencarian", command=self.start_scan, bg="lightgray", font=("Arial", 10, "bold"))
        self.btn_scan.grid(row=0, column=2, rowspan=3, padx=20, sticky="nsew")

        self.lbl_status = tk.Label(top_frame, text="Status: Menunggu...", fg="gray")
        self.lbl_status.grid(row=0, column=3, rowspan=3, padx=10)

        # --- Middle Frame for Results ---
        mid_frame = tk.Frame(self.root, padx=10, pady=5)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ukuran", "nama", "path_a", "path_b", "date_a", "date_b")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("ukuran", text="Ukuran")
        self.tree.column("ukuran", width=80, anchor="e")
        self.tree.heading("nama", text="Nama File Asli")
        self.tree.column("nama", width=150)
        self.tree.heading("path_a", text="Lokasi Persis A")
        self.tree.column("path_a", width=250)
        self.tree.heading("path_b", text="Lokasi Persis B")
        self.tree.column("path_b", width=250)
        self.tree.heading("date_a", text="Tanggal A")
        self.tree.column("date_a", width=120)
        self.tree.heading("date_b", text="Tanggal B")
        self.tree.column("date_b", width=120)

        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Bottom Frame for Actions ---
        bot_frame = tk.Frame(self.root, pady=10)
        bot_frame.pack(fill=tk.X)

        btn_open_a = tk.Button(bot_frame, text="Buka Lokasi A", command=lambda: self.open_location('A'))
        btn_open_a.pack(side=tk.LEFT, padx=10)
        
        btn_open_b = tk.Button(bot_frame, text="Buka Lokasi B", command=lambda: self.open_location('B'))
        btn_open_b.pack(side=tk.LEFT, padx=10)

        btn_del_a = tk.Button(bot_frame, text="Hapus File di Lokasi A", command=lambda: self.delete_file('A'), fg="red")
        btn_del_a.pack(side=tk.LEFT, padx=30)

        btn_del_b = tk.Button(bot_frame, text="Hapus File di Lokasi B", command=lambda: self.delete_file('B'), fg="red")
        btn_del_b.pack(side=tk.LEFT, padx=10)

        btn_keep = tk.Button(bot_frame, text="Pertahankan Keduanya (Abaikan)", command=self.keep_both)
        btn_keep.pack(side=tk.RIGHT, padx=10)

    def select_dir(self, dir_type):
        folder = filedialog.askdirectory()
        if folder:
            if dir_type == 'A':
                self.dir_a = folder
                self.lbl_dir_a.config(text=f"Lokasi A: {self.dir_a}")
            else:
                self.dir_b = folder
                self.lbl_dir_b.config(text=f"Lokasi B: {self.dir_b}")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def format_date(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def get_file_hash(self, filepath):
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
            
    def get_files_from_dir(self, base_dir, label):
        file_dict = {}
        skip_hidden = self.skip_hidden_var.get()
        skip_gitignore = self.skip_gitignore_var.get()
        
        # Menyimpan rules .gitignore secara hirarki
        ignore_rules_map = {}
        
        for root, dirs, files in os.walk(base_dir):
            # 1. Melewati file & folder tersembunyi
            if skip_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
                
            # 2. Mengumpulkan dan menerapkan aturan .gitignore
            if skip_gitignore:
                local_rules = []
                gitignore_path = os.path.join(root, '.gitignore')
                
                # Baca file .gitignore di folder saat ini jika ada
                if os.path.exists(gitignore_path):
                    try:
                        with open(gitignore_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                # Abaikan baris kosong atau komentar
                                if line and not line.startswith('#'):
                                    local_rules.append(line)
                    except:
                        pass
                
                # Warisi aturan dari folder di atasnya (parent)
                parent_dir = os.path.dirname(root)
                current_rules = ignore_rules_map.get(parent_dir, []) + local_rules
                ignore_rules_map[root] = current_rules
                
                # Fungsi untuk mengecek apakah suatu nama file/folder masuk dalam daftar ignore
                def is_ignored(name):
                    rel_path = os.path.relpath(os.path.join(root, name), base_dir).replace('\\', '/')
                    for rule in current_rules:
                        r = rule.strip('/')
                        # Pencocokan pola dasar (Wildcard/Exact)
                        if fnmatch.fnmatch(name, rule) or fnmatch.fnmatch(name, r):
                            return True
                        if fnmatch.fnmatch(rel_path, rule) or fnmatch.fnmatch(rel_path, r):
                            return True
                        # Menangani rule direktori seperti folder/ atau folder/*
                        if fnmatch.fnmatch(rel_path, r + '/*'):
                            return True
                    return False

                # Modifikasi list dirs dan files agar os.walk tidak memprosesnya
                dirs[:] = [d for d in dirs if not is_ignored(d)]
                files = [f for f in files if not is_ignored(f)]

            # Kumpulkan file yang lolos filter
            for file in files:
                path = os.path.join(root, file)
                try:
                    stat = os.stat(path)
                    size = stat.st_size
                    if size not in file_dict:
                        file_dict[size] = []
                    file_dict[size].append({'path': path, 'stat': stat, 'name': file})
                except:
                    pass
                    
        return file_dict

    def start_scan(self):
        if not self.dir_a or not self.dir_b:
            messagebox.showwarning("Peringatan", "Harap pilih Lokasi A dan Lokasi B terlebih dahulu!")
            return
        
        self.tree.delete(*self.tree.get_children())
        self.btn_scan.config(state=tk.DISABLED)
        self.lbl_status.config(text="Status: Mempersiapkan pencarian...", fg="blue")
        
        threading.Thread(target=self.scan_process, daemon=True).start()

    def scan_process(self):
        self.root.after(0, lambda: self.lbl_status.config(text="Status: Membaca dan memfilter Lokasi A..."))
        dict_a = self.get_files_from_dir(self.dir_a, 'A')

        self.root.after(0, lambda: self.lbl_status.config(text="Status: Membaca dan memfilter Lokasi B..."))
        dict_b = self.get_files_from_dir(self.dir_b, 'B')

        # Tahap 2: Bandingkan isi file yang ukurannya sama persis
        common_sizes = set(dict_a.keys()).intersection(set(dict_b.keys()))
        total_sizes = len(common_sizes)
        
        results = []
        
        for i, size in enumerate(common_sizes):
            if i % max(1, total_sizes // 20) == 0:
                self.root.after(0, lambda i=i, t=total_sizes: self.lbl_status.config(text=f"Status: Mencocokkan isi file ({i}/{t})..."))
            
            # Hitung hash untuk file di A
            hash_a = {}
            for file_a in dict_a[size]:
                f_hash = self.get_file_hash(file_a['path'])
                if f_hash:
                    if f_hash not in hash_a: hash_a[f_hash] = []
                    hash_a[f_hash].append(file_a)

            # Hitung hash untuk file di B & cari duplikat
            for file_b in dict_b[size]:
                f_hash = self.get_file_hash(file_b['path'])
                if f_hash and f_hash in hash_a:
                    for match_a in hash_a[f_hash]:
                        ext_a = os.path.splitext(match_a['name'])[1].lower()
                        ext_b = os.path.splitext(file_b['name'])[1].lower()
                        if ext_a == ext_b:
                            results.append({
                                'size': size,
                                'file_a': match_a,
                                'file_b': file_b
                            })

        self.root.after(0, lambda: self.populate_tree(results))

    def populate_tree(self, results):
        results.sort(key=lambda x: x['file_a']['path'])
        
        for res in results:
            self.tree.insert("", tk.END, values=(
                self.format_size(res['size']),
                res['file_a']['name'],
                res['file_a']['path'],
                res['file_b']['path'],
                self.format_date(res['file_a']['stat'].st_mtime),
                self.format_date(res['file_b']['stat'].st_mtime)
            ))
            
        self.lbl_status.config(text=f"Status: Selesai! Ditemukan {len(results)} file duplikat.", fg="green")
        self.btn_scan.config(state=tk.NORMAL)

    def open_location(self, loc_type):
        selected = self.tree.selection()
        if not selected:
            return
        
        for item in selected:
            values = self.tree.item(item, "values")
            path = values[2] if loc_type == 'A' else values[3]
            dir_path = os.path.dirname(path)
            
            try:
                if platform.system() == "Windows":
                    os.startfile(dir_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", dir_path])
                else:
                    subprocess.Popen(["xdg-open", dir_path])
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka lokasi:\n{e}")

    def delete_file(self, loc_type):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih file dari daftar terlebih dahulu!")
            return

        count = len(selected)
        msg = f"Apakah Anda yakin ingin menghapus {count} file pada LOKASI {loc_type} secara permanen?\n\nFile dari list yang dipilih akan terhapus dari harddisk!"
        if messagebox.askyesno("Konfirmasi Hapus", msg):
            for item in selected:
                values = self.tree.item(item, "values")
                path = values[2] if loc_type == 'A' else values[3]
                
                try:
                    if os.path.exists(path):
                        os.remove(path)
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menghapus file:\n{path}\n\n{e}")

    def keep_both(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()