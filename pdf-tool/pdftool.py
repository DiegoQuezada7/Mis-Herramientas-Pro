import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Listbox
from tkinterdnd2 import DND_FILES, TkinterDnD
import fitz  # PyMuPDF
import os

class PDFToolApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Swiss Knife 📄🔪")
        self.geometry("600x500")
        self.configure(bg="#1e1e1e")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white", padding=[15, 5], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", "#007fd4")])
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TButton", font=("Segoe UI", 9, "bold"))
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_merge = ttk.Frame(self.notebook)
        self.tab_split = ttk.Frame(self.notebook)
        self.tab_images = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_merge, text=" 🔗 Unir (Merge) ")
        self.notebook.add(self.tab_split, text=" ✂️ Cortar/Separar ")
        self.notebook.add(self.tab_images, text=" 🖼️ Extraer Imágenes ")
        
        self._setup_merge_tab()
        self._setup_split_tab()
        self._setup_images_tab()
        
    def _setup_merge_tab(self):
        # Lista de archivos
        frame_list = tk.Frame(self.tab_merge, bg="#1e1e1e")
        frame_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lst_merge = Listbox(frame_list, bg="#252526", fg="white", selectbackground="#007fd4", bd=0, highlightthickness=1, font=("Consolas", 9))
        self.lst_merge.pack(side="left", fill="both", expand=True)
        
        sb = tk.Scrollbar(frame_list, orient="vertical", command=self.lst_merge.yview)
        sb.pack(side="right", fill="y")
        self.lst_merge.config(yscrollcommand=sb.set)
        
        # Drag & Drop
        self.lst_merge.drop_target_register(DND_FILES)
        self.lst_merge.dnd_bind('<<Drop>>', self.on_drop_merge)
        
        lbl_hint = tk.Label(self.tab_merge, text="Arrastra tus PDFs aquí para unirlos", fg="#888", bg="#1e1e1e")
        lbl_hint.pack()

        # Botones Control
        frame_btns = tk.Frame(self.tab_merge, bg="#1e1e1e")
        frame_btns.pack(fill="x", padx=10, pady=15)
        
        tk.Button(frame_btns, text="⬆ Subir", command=lambda: self.move_item(-1), bg="#3e3e42", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(frame_btns, text="⬇ Bajar", command=lambda: self.move_item(1), bg="#3e3e42", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(frame_btns, text="🗑️ Quitar", command=self.remove_item, bg="#3e3e42", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(frame_btns, text="🔥 UNIR PDFS", command=self.merge_pdfs, bg="#007fd4", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20).pack(side="right", padx=5)

    def _setup_split_tab(self):
        self.frame_split_drop = tk.Frame(self.tab_split, bg="#252526", width=400, height=150, highlightthickness=2, highlightbackground="#444")
        self.frame_split_drop.pack(pady=30)
        self.frame_split_drop.pack_propagate(False)
        
        self.lbl_split_file = tk.Label(self.frame_split_drop, text="Arrastra 1 PDF aquí", fg="#aaa", bg="#252526", font=("Segoe UI", 12))
        self.lbl_split_file.place(relx=0.5, rely=0.5, anchor="center")
        
        self.frame_split_drop.drop_target_register(DND_FILES)
        self.frame_split_drop.dnd_bind('<<Drop>>', self.on_drop_split)
        
        # Opciones
        frame_opts = tk.Frame(self.tab_split, bg="#1e1e1e")
        frame_opts.pack(pady=10)
        
        tk.Label(frame_opts, text="Páginas (ej: 1, 3-5, 8):", bg="#1e1e1e", fg="white").pack(anchor="w")
        self.entry_range = tk.Entry(frame_opts, width=40, font=("Consolas", 11), bg="#333", fg="white", insertbackground="white")
        self.entry_range.pack(pady=5)
        
        tk.Button(self.tab_split, text="✂️ EXTRAER PÁGINAS", command=self.split_pdf, bg="#007fd4", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=10).pack(pady=20)
        
        self.current_split_file = None

    def _setup_images_tab(self):
        self.frame_img_drop = tk.Frame(self.tab_images, bg="#252526", width=400, height=150, highlightthickness=2, highlightbackground="#444")
        self.frame_img_drop.pack(pady=30)
        self.frame_img_drop.pack_propagate(False)
        
        self.lbl_img_file = tk.Label(self.frame_img_drop, text="Arrastra 1 PDF aquí", fg="#aaa", bg="#252526", font=("Segoe UI", 12))
        self.lbl_img_file.place(relx=0.5, rely=0.5, anchor="center")
        
        self.frame_img_drop.drop_target_register(DND_FILES)
        self.frame_img_drop.dnd_bind('<<Drop>>', self.on_drop_img)
        
        tk.Button(self.tab_images, text="🖼️ EXTRAER TODAS LAS IMÁGENES", command=self.extract_images, bg="#007fd4", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=10).pack(pady=20)
        
        self.current_img_file = None

    # --- Logic Merge ---
    def on_drop_merge(self, event):
        files = self.split_file_list(event.data)
        for f in files:
            if f.lower().endswith('.pdf'):
                self.lst_merge.insert(tk.END, f)
                
    def move_item(self, direction):
        idxs = self.lst_merge.curselection()
        if not idxs: return
        idx = idxs[0]
        if direction == -1 and idx > 0:
            text = self.lst_merge.get(idx)
            self.lst_merge.delete(idx)
            self.lst_merge.insert(idx-1, text)
            self.lst_merge.selection_set(idx-1)
        elif direction == 1 and idx < self.lst_merge.size()-1:
            text = self.lst_merge.get(idx)
            self.lst_merge.delete(idx)
            self.lst_merge.insert(idx+1, text)
            self.lst_merge.selection_set(idx+1)
            
    def remove_item(self):
        idxs = self.lst_merge.curselection()
        if idxs: self.lst_merge.delete(idxs[0])
        
    def merge_pdfs(self):
        files = self.lst_merge.get(0, tk.END)
        if not files: return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return
        
        try:
            doc_merged = fitz.open()
            for pdf in files:
                with fitz.open(pdf) as doc:
                    doc_merged.insert_pdf(doc)
            
            doc_merged.save(save_path)
            messagebox.showinfo("Éxito", "¡PDFs unidos correctamente!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Logic Split ---
    def on_drop_split(self, event):
        files = self.split_file_list(event.data)
        if files and files[0].lower().endswith('.pdf'):
            self.current_split_file = files[0]
            self.lbl_split_file.config(text=os.path.basename(self.current_split_file), fg="white")

    def split_pdf(self):
        if not self.current_split_file: return
        page_range_str = self.entry_range.get().strip()
        if not page_range_str: return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return
        
        try:
            doc_src = fitz.open(self.current_split_file)
            doc_new = fitz.open()
            
            # Parsear rangos: "1, 3-5" -> [0, 2, 3, 4] (0-indexed)
            pages_to_keep = set()
            parts = page_range_str.split(',')
            for p in parts:
                p = p.strip()
                if '-' in p:
                    start, end = map(int, p.split('-'))
                    for i in range(start, end+1):
                        pages_to_keep.add(i-1)
                else:
                    pages_to_keep.add(int(p)-1)
            
            sorted_pages = sorted(list(pages_to_keep))
            
            for page_num in sorted_pages:
                if 0 <= page_num < len(doc_src):
                    doc_new.insert_pdf(doc_src, from_page=page_num, to_page=page_num)
            
            doc_new.save(save_path)
            messagebox.showinfo("Éxito", "¡Páginas extraídas!")
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando: {e}")

    # --- Logic Images ---
    def on_drop_img(self, event):
        files = self.split_file_list(event.data)
        if files and files[0].lower().endswith('.pdf'):
            self.current_img_file = files[0]
            self.lbl_img_file.config(text=os.path.basename(self.current_img_file), fg="white")

    def extract_images(self):
        if not self.current_img_file: return
        
        save_dir = filedialog.askdirectory(title="Selecciona Carpeta de Destino")
        if not save_dir: return
        
        try:
            doc = fitz.open(self.current_img_file)
            count = 0
            for i in range(len(doc)):
                page = doc[i]
                images = page.get_images()
                for img in images:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    filename = os.path.join(save_dir, f"img_p{i+1}_{xref}.{ext}")
                    with open(filename, "wb") as f:
                        f.write(image_bytes)
                    count += 1
            
            messagebox.showinfo("Éxito", f"¡Se extrajeron {count} imágenes!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def split_file_list(self, data):
        if data.startswith('{'):
            return [x.strip('{}') for x in data.split('} {')]
        return data.split()

if __name__ == "__main__":
    app = PDFToolApp()
    app.mainloop()
