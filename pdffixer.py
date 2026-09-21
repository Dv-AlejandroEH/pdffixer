import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pymupdf as fitz
from PIL import Image, ImageTk, ImageOps
import io
import warnings

# --- Configuración de Seguridad y Errores ---
fitz.TOOLS.mupdf_display_errors(False)
Image.MAX_IMAGE_PIXELS = None 
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

class PDFFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor Visual de Cortes PDF (Versión Optimizada)")
        self.root.geometry("1080x780")

        self.doc = None
        self.pdf_path = ""
        self.current_page_idx = 0
        self.pages_data = []
        
        self.cut_ratio = tk.DoubleVar(value=0.25)
        self.action_var = tk.StringVar(value="NONE")
        self.mirror_var = tk.BooleanVar(value=False)
        
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.rect_id = None
        
        # Caché para fluidez en el canvas
        self.base_preview_img = None
        self.cached_thumbnail = None
        self.displayed_img_size = (0, 0)

        self._build_ui()

    def _build_ui(self):
        # Panel Superior
        top_bar = tk.Frame(self.root, pady=10)
        top_bar.pack(fill=tk.X, side=tk.TOP, padx=10)

        tk.Button(top_bar, text="📁 Cargar PDF", command=self.load_pdf, font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        self.lbl_file = tk.Label(top_bar, text="Ningún archivo cargado", fg="gray")
        self.lbl_file.pack(side=tk.LEFT, padx=10)

        tk.Button(top_bar, text="💾 Exportar PDF Arreglado", command=self.export_pdf, bg="#2e7d32", fg="white", font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=5)

        # Contenedor Principal
        main_box = tk.Frame(self.root)
        main_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Panel Izquierdo: Canvas
        self.canvas_frame = tk.Frame(main_box, bg="#333")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#222")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Configure>", lambda e: self.rebuild_thumbnail() if self.doc else None)

        # Panel Derecho: Ajustes
        sidebar = tk.Frame(main_box, width=340, padx=15, pady=10)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(sidebar, text="Navegación", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Buscador de páginas
        nav_box = tk.Frame(sidebar, pady=5)
        nav_box.pack(fill=tk.X)
        tk.Button(nav_box, text="◄ Ant", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        
        self.page_entry = tk.Entry(nav_box, width=5, justify="center")
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind('<Return>', self.goto_page)
        tk.Button(nav_box, text="Ir", command=self.goto_page).pack(side=tk.LEFT, padx=2)
        
        tk.Button(nav_box, text="Sig ►", command=self.next_page).pack(side=tk.RIGHT, padx=2)

        self.lbl_page_num = tk.Label(sidebar, text="Página: - / -", font=("Arial", 10, "italic"), pady=5)
        self.lbl_page_num.pack(anchor="w")

        tk.Frame(sidebar, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=8)

        # Controles de Página (Rotar y Eliminar)
        tk.Label(sidebar, text="Gestión de Página", font=("Arial", 11, "bold")).pack(anchor="w")
        page_ops_box = tk.Frame(sidebar, pady=5)
        page_ops_box.pack(fill=tk.X)
        
        tk.Button(page_ops_box, text="🔄 Rotar 90°", command=self.rotate_page, bg="#1976d2", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(page_ops_box, text="🗑️ Eliminar Página", command=self.delete_current_page, bg="#d32f2f", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

        tk.Frame(sidebar, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=8)
        
        tk.Checkbutton(sidebar, text="🪞 Efecto Espejo (Reflejar)", variable=self.mirror_var, command=self.on_mirror_change, font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        
        tk.Frame(sidebar, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=8)

        tk.Label(sidebar, text="Acción de corte:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        actions = [
            ("Sin modificar (Página completa)", "NONE"),
            ("✂️ Recortar área (Dibuja un cuadrado)", "CROP"),
            ("⬆ Subir trozo sup. a la pág. anterior", "MOVE_TOP_UP"),
            ("⬇ Bajar trozo inf. a la pág. siguiente", "MOVE_BOTTOM_DOWN")
        ]
        
        for text, mode in actions:
            rb = tk.Radiobutton(sidebar, text=text, value=mode, variable=self.action_var, 
                                command=self.on_action_change, wraplength=300, justify="left", anchor="w")
            rb.pack(fill=tk.X, pady=3)

        tk.Frame(sidebar, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=8)

        tk.Label(sidebar, text="Ajuste fino de la línea:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.slider = ttk.Scale(sidebar, from_=0.05, to=0.95, variable=self.cut_ratio, command=self.on_slider_move)
        self.slider.pack(fill=tk.X, pady=5)

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if not path: return
        
        self.pdf_path = path
        self.doc = fitz.open(path)
        self.lbl_file.config(text=path.split("/")[-1], fg="black")

        self.pages_data = []
        for _ in range(len(self.doc)):
            self.pages_data.append({
                "action": "NONE",
                "cut_ratio": 0.25,
                "mirror": False,
                "rotation": 0,
                "crop_box": (0, 0, 1, 1)
            })

        self.current_page_idx = 0
        self.load_page_into_ui()

    def load_page_into_ui(self):
        if not self.doc or len(self.doc) == 0: return
        data = self.pages_data[self.current_page_idx]
        
        self.action_var.set(data.get("action", "NONE"))
        self.cut_ratio.set(data.get("cut_ratio", 0.25))
        self.mirror_var.set(data.get("mirror", False))
        
        rot = data.get("rotation", 0)
        self.lbl_page_num.config(text=f"Página: {self.current_page_idx + 1} de {len(self.doc)} (Rot: {rot}°)")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page_idx + 1))
        
        page = self.doc[self.current_page_idx]
        pix = page.get_pixmap(dpi=75) 
        self.base_preview_img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        self.rebuild_thumbnail()

    def rebuild_thumbnail(self):
        if not self.base_preview_img: return
        
        img = self.base_preview_img.copy()
        
        # Aplicar rotación y espejo en la vista previa
        rot = self.pages_data[self.current_page_idx].get("rotation", 0)
        if rot != 0:
            img = img.rotate(-rot, expand=True)
            
        if self.mirror_var.get():
            img = ImageOps.mirror(img)

        canvas_w = self.canvas.winfo_width() or 600
        canvas_h = self.canvas.winfo_height() or 650
        
        img.thumbnail((canvas_w - 20, canvas_h - 20))
        self.cached_thumbnail = ImageTk.PhotoImage(img)
        self.displayed_img_size = img.size
        
        self.update_canvas_view()

    def update_canvas_view(self):
        if not self.cached_thumbnail: return
        self.canvas.delete("all")
        
        canvas_w = self.canvas.winfo_width() or 600
        canvas_h = self.canvas.winfo_height() or 650
        
        self.img_offset_x = (canvas_w - self.displayed_img_size[0]) // 2
        self.img_offset_y = (canvas_h - self.displayed_img_size[1]) // 2
        
        self.canvas.create_image(self.img_offset_x, self.img_offset_y, anchor="nw", image=self.cached_thumbnail)

        action = self.action_var.get()
        if action in ["MOVE_TOP_UP", "MOVE_BOTTOM_DOWN"]:
            y_line = self.img_offset_y + int(self.displayed_img_size[1] * self.cut_ratio.get())
            color = "#d32f2f" if action == "MOVE_TOP_UP" else "#1976d2"
            self.canvas.create_line(self.img_offset_x, y_line, self.img_offset_x + self.displayed_img_size[0], y_line, fill=color, width=3, dash=(6, 4))
            
        elif action == "CROP":
            cb = self.pages_data[self.current_page_idx].get("crop_box", (0, 0, 1, 1))
            if cb != (0, 0, 1, 1):
                x0 = self.img_offset_x + int(cb[0] * self.displayed_img_size[0])
                y0 = self.img_offset_y + int(cb[1] * self.displayed_img_size[1])
                x1 = self.img_offset_x + int(cb[2] * self.displayed_img_size[0])
                y1 = self.img_offset_y + int(cb[3] * self.displayed_img_size[1])
                self.rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="#4caf50", width=3, dash=(4, 4))

    def rotate_page(self):
        if not self.doc: return
        self.save_current_page_state()
        curr_rot = self.pages_data[self.current_page_idx].get("rotation", 0)
        new_rot = (curr_rot + 90) % 360
        self.pages_data[self.current_page_idx]["rotation"] = new_rot
        self.load_page_into_ui()

    def delete_current_page(self):
        if not self.doc: return
        if len(self.doc) <= 1:
            messagebox.showwarning("Aviso", "No puedes eliminar la última página restante del documento.")
            return
        
        if messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar la página {self.current_page_idx + 1}?"):
            self.doc.delete_page(self.current_page_idx)
            self.pages_data.pop(self.current_page_idx)
            
            if self.current_page_idx >= len(self.doc):
                self.current_page_idx = len(self.doc) - 1
                
            self.load_page_into_ui()

    def on_mouse_down(self, event):
        if not self.doc: return
        action = self.action_var.get()
        if action in ["MOVE_TOP_UP", "MOVE_BOTTOM_DOWN"]:
            self.update_cut_line(event.y)
        elif action == "CROP":
            self.crop_start_x = event.x
            self.crop_start_y = event.y
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y, outline="#4caf50", width=3, dash=(4, 4))

    def on_mouse_drag(self, event):
        if not self.doc: return
        action = self.action_var.get()
        if action in ["MOVE_TOP_UP", "MOVE_BOTTOM_DOWN"]:
            self.update_cut_line(event.y)
        elif action == "CROP" and self.rect_id:
            self.canvas.coords(self.rect_id, self.crop_start_x, self.crop_start_y, event.x, event.y)

    def on_mouse_up(self, event):
        if not self.doc: return
        action = self.action_var.get()
        if action == "CROP" and self.rect_id:
            img_w, img_h = self.displayed_img_size
            x0 = min(self.crop_start_x, event.x) - self.img_offset_x
            y0 = min(self.crop_start_y, event.y) - self.img_offset_y
            x1 = max(self.crop_start_x, event.x) - self.img_offset_x
            y1 = max(self.crop_start_y, event.y) - self.img_offset_y
            
            x0, y0 = max(0, min(img_w, x0)), max(0, min(img_h, y0))
            x1, y1 = max(0, min(img_w, x1)), max(0, min(img_h, y1))
            
            if x1 > x0 and y1 > y0:
                self.pages_data[self.current_page_idx]["crop_box"] = (x0/img_w, y0/img_h, x1/img_w, y1/img_h)
            
            self.save_current_page_state()
            self.update_canvas_view()

    def update_cut_line(self, y_event):
        img_h = self.displayed_img_size[1]
        y_rel = y_event - self.img_offset_y
        if 0 <= y_rel <= img_h:
            self.cut_ratio.set(round(y_rel / img_h, 3))
            self.save_current_page_state()
            self.update_canvas_view()

    def on_slider_move(self, val):
        if self.doc and self.action_var.get() in ["MOVE_TOP_UP", "MOVE_BOTTOM_DOWN"]:
            self.save_current_page_state()
            self.update_canvas_view()

    def on_action_change(self):
        if self.doc:
            self.save_current_page_state()
            self.update_canvas_view()
            
    def on_mirror_change(self):
        if self.doc:
            self.save_current_page_state()
            self.rebuild_thumbnail()

    def save_current_page_state(self):
        if self.doc and self.current_page_idx < len(self.pages_data):
            self.pages_data[self.current_page_idx]["action"] = self.action_var.get()
            self.pages_data[self.current_page_idx]["cut_ratio"] = self.cut_ratio.get()
            self.pages_data[self.current_page_idx]["mirror"] = self.mirror_var.get()

    def goto_page(self, event=None):
        if not self.doc: return
        try:
            num = int(self.page_entry.get()) - 1
            if 0 <= num < len(self.doc):
                self.save_current_page_state()
                self.current_page_idx = num
                self.load_page_into_ui()
            else:
                messagebox.showwarning("Aviso", f"Página fuera de rango (1 a {len(self.doc)})")
        except ValueError:
            pass

    def prev_page(self):
        if self.doc and self.current_page_idx > 0:
            self.save_current_page_state()
            self.current_page_idx -= 1
            self.load_page_into_ui()

    def next_page(self):
        if self.doc and self.current_page_idx < len(self.doc) - 1:
            self.save_current_page_state()
            self.current_page_idx += 1
            self.load_page_into_ui()

    def export_pdf(self):
        if not self.doc: return
        self.save_current_page_state()
        
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivo PDF", "*.pdf")])
        if not output_path: return

        out_pdf = fitz.open()
        pending_bottom_chunk = None
        prev_page_img = None

        def save_img_to_pdf(pil_img):
            b = io.BytesIO()
            pil_img.save(b, format="PDF", resolution=150)
            temp_doc = fitz.open("pdf", b.getvalue())
            out_pdf.insert_pdf(temp_doc)
            temp_doc.close()

        for i in range(len(self.doc)):
            cfg = self.pages_data[i]
            
            pix = self.doc[i].get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Aplicar rotación y espejo
            rot = cfg.get("rotation", 0)
            if rot != 0:
                img = img.rotate(-rot, expand=True)
            if cfg.get("mirror", False):
                img = ImageOps.mirror(img)
                
            w, h = img.size
            action = cfg.get("action", "NONE")
            
            if action == "CROP":
                cb = cfg.get("crop_box", (0, 0, 1, 1))
                crop_px = (int(cb[0]*w), int(cb[1]*h), int(cb[2]*w), int(cb[3]*h))
                
                if crop_px[2] > crop_px[0] and crop_px[3] > crop_px[1]:
                    current_base = img.crop(crop_px)
                else:
                    current_base = img

            elif action == "MOVE_TOP_UP":
                y_cut = int(h * cfg["cut_ratio"])
                chunk_to_up = img.crop((0, 0, w, y_cut))
                current_base = img.crop((0, y_cut, w, h))
                
                if prev_page_img is not None:
                    new_w = max(prev_page_img.width, chunk_to_up.width)
                    new_h = prev_page_img.height + chunk_to_up.height
                    merged = Image.new("RGB", (new_w, new_h), (255, 255, 255))
                    merged.paste(prev_page_img, (0, 0))
                    merged.paste(chunk_to_up, (0, prev_page_img.height))
                    prev_page_img = merged

            elif action == "MOVE_BOTTOM_DOWN":
                y_cut = int(h * cfg["cut_ratio"])
                current_base = img.crop((0, 0, w, y_cut))
                new_pending_bottom = img.crop((0, y_cut, w, h))

            else:  
                current_base = img

            if pending_bottom_chunk is not None and action != "MOVE_BOTTOM_DOWN":
                new_w = max(current_base.width, pending_bottom_chunk.width)
                new_h = pending_bottom_chunk.height + current_base.height
                merged = Image.new("RGB", (new_w, new_h), (255, 255, 255))
                merged.paste(pending_bottom_chunk, (0, 0))
                merged.paste(current_base, (0, pending_bottom_chunk.height))
                current_base = merged
                pending_bottom_chunk = None

            if action == "MOVE_BOTTOM_DOWN":
                pending_bottom_chunk = new_pending_bottom

            if prev_page_img is not None:
                save_img_to_pdf(prev_page_img)

            prev_page_img = current_base

        if prev_page_img is not None:
            save_img_to_pdf(prev_page_img)
        if pending_bottom_chunk is not None:
            save_img_to_pdf(pending_bottom_chunk)

        out_pdf.save(output_path)
        out_pdf.close()
        messagebox.showinfo("Éxito", "PDF generado, rotado y reordenado correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFFixerApp(root)
    root.mainloop()
