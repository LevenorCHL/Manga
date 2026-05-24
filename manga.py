import os
import re
import zipfile
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF

class MangaImpositionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manga & Book Imposition Tool (Listo para Imprenta)")
        self.root.geometry("650x480")
        self.root.resizable(False, False)
        
        # Variables de control
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.paper_size = tk.StringVar(value="Carta (216 x 279 mm)")
        self.reading_order = tk.StringVar(value="Manga / Oriental (RTL)")
        self.sig_size = tk.StringVar(value="Cuadernillos de 16 páginas")
        self.gutter_mm = tk.DoubleVar(value=5.0)  # Espacio extra en el centro para el pegado
        
        self.create_widgets()

    def create_widgets(self):
        # Panel de Archivos
        file_frame = ttk.LabelFrame(self.root, text=" Archivos ", padding=15)
        file_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(file_frame, text="Origen (.cbz, .pdf):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=52).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Buscar", command=self.browse_input).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="Destino Imposición:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path, width=52).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Guardar como", command=self.browse_output).grid(row=1, column=2)

        # Panel de Configuración de Imprenta
        print_frame = ttk.LabelFrame(self.root, text=" Configuración de Pliegos e Imposición ", padding=15)
        print_frame.pack(fill="x", padx=15, pady=5)
        
        # Tipo de papel físico de la impresora
        ttk.Label(print_frame, text="Papel de la Impresora:").grid(row=0, column=0, sticky="w", pady=5)
        paper_combo = ttk.Combobox(print_frame, textvariable=self.paper_size, values=["Carta (216 x 279 mm)", "A4 (210 x 297 mm)"], state="readonly", width=28)
        paper_combo.grid(row=0, column=1, sticky="w", padx=5)
        
        # Orden de lectura
        ttk.Label(print_frame, text="Orden de Lectura:").grid(row=1, column=0, sticky="w", pady=5)
        reading_combo = ttk.Combobox(print_frame, textvariable=self.reading_order, values=["Manga / Oriental (RTL)", "Occidental (LTR)"], state="readonly", width=28)
        reading_combo.grid(row=1, column=1, sticky="w", padx=5)
        
        # Tamaño del cuadernillo para el pegado
        ttk.Label(print_frame, text="Estructura de Cuadernillo:").grid(row=2, column=0, sticky="w", pady=5)
        sig_combo = ttk.Combobox(print_frame, textvariable=self.sig_size, values=["Cuadernillos de 16 páginas", "Cuadernillos de 32 páginas", "Folleto Único (Todo en uno)"], state="readonly", width=28)
        sig_combo.grid(row=2, column=1, sticky="w", padx=5)
        
        # Margen de lomo para la cola
        ttk.Label(print_frame, text="Margen de Lomo / Gutter (mm):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(print_frame, textvariable=self.gutter_mm, width=10).grid(row=3, column=1, sticky="w", padx=5)

        # Barra de progreso y botón de acción
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=20)
        
        self.btn_process = ttk.Button(self.root, text="Generar PDF Impuesto para Libro", command=self.process_imposition)
        self.btn_process.pack(pady=5)

    def browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos soportados", "*.cbz *.pdf"), ("Manga .cbz", "*.cbz"), ("Documento .pdf", "*.pdf")])
        if path:
            self.input_path.set(path)
            base, _ = os.path.splitext(path)
            self.output_path.set(f"{base}_IMPUESTO_CARTA.pdf")

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Documento PDF", "*.pdf")])
        if path:
            self.output_path.set(path)

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def mm_to_points(self, mm):
        return (mm / 25.4) * 72

    def process_imposition(self):
        in_p = self.input_path.get()
        out_p = self.output_path.get()
        
        if not in_p or not out_p:
            messagebox.showerror("Error", "Por favor, selecciona los archivos de entrada y salida.")
            return
        
        self.btn_process.config(state="disabled")
        self.progress["value"] = 0
        self.root.update_idletasks()
        
        try:
            # 1. Normalizar entrada a un PDF secuencial temporal en memoria
            doc_temp = fitz.open()
            
            if in_p.lower().endswith('.cbz'):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(in_p, 'r') as archive:
                        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.tiff')
                        img_files = [f for f in archive.namelist() if f.lower().endswith(valid_extensions) and not f.startswith('__MACOSX')]
                        img_files.sort(key=self.natural_sort_key)
                        
                        if not img_files:
                            raise ValueError("El archivo .cbz no contiene imágenes válidas.")
                        
                        for img_name in img_files:
                            archive.extract(img_name, temp_dir)
                            full_path = os.path.join(temp_dir, img_name)
                            # Abrimos la imagen de forma nativa para respetar sus dimensiones de proporción
                            img_doc = fitz.open(full_path)
                            img_rect = img_doc[0].rect
                            page = doc_temp.new_page(width=img_rect.width, height=img_rect.height)
                            page.insert_image(img_rect, filename=full_path)
                            img_doc.close()
            else:
                doc_temp = fitz.open(in_p)

            # 2. Calcular tamaño del cuadernillo (debe ser múltiplo de 4)
            total_initial_pages = len(doc_temp)
            sig_choice = self.sig_size.get()
            
            if "16" in sig_choice:
                sig_size = 16
            elif "32" in sig_choice:
                sig_size = 32
            else:  # Folleto único
                sig_size = ((total_initial_pages + 3) // 4) * 4
                
            # Rellenar con páginas en blanco si el documento no es múltiplo del cuadernillo elegido
            while len(doc_temp) % sig_size != 0:
                doc_temp.new_page()
                
            total_pages = len(doc_temp)
            
            # 3. Configurar lienzo físico (Carta o A4 en Horizontal/Landscape)
            if "Carta" in self.paper_size.get():
                w_mm, h_mm = 279.4, 215.9  # Hoja Carta Horizontal
            else:
                w_mm, h_mm = 297.0, 210.0  # Hoja A4 Horizontal
                
            w_pt = self.mm_to_points(w_mm)
            h_pt = self.mm_to_points(h_mm)
            center_x = w_pt / 2
            
            # Definir márgenes de cortesía e lomo (Gutter)
            gutter = self.mm_to_points(self.gutter_mm.get())
            margin = self.mm_to_points(6.0) # 6mm de margen externo de seguridad
            
            # Rectángulos destino en el pliego físico (izquierdo y derecho)
            # El lomo está en el centro, por lo que el gutter se resta/suma desde el eje central
            rect_left = fitz.Rect(margin, margin, center_x - gutter, h_pt - margin)
            rect_right = fitz.Rect(center_x + gutter, margin, w_pt - margin, h_pt - margin)
            
            # 4. Algoritmo de Imposición por Cuadernillos
            doc_out = fitz.open()
            is_rtl = "RTL" in self.reading_order.get()
            
            num_signatures = total_pages // sig_size
            
            for sig_idx in range(num_signatures):
                sig_start = sig_idx * sig_size
                sheets_in_sig = sig_size // 4
                
                for i in range(sheets_in_sig):
                    # --- CARA FRENTE (Impresión Impar) ---
                    page_front = doc_out.new_page(width=w_pt, height=h_pt)
                    
                    if not is_rtl: # LTR Occidental
                        left_src = sig_start + (sig_size - 2 * i - 1)
                        right_src = sig_start + (2 * i)
                    else:          # RTL Manga
                        left_src = sig_start + (2 * i)
                        right_src = sig_start + (sig_size - 2 * i - 1)
                        
                    page_front.show_pdf_page(rect_left, doc_temp, left_src)
                    page_front.show_pdf_page(rect_right, doc_temp, right_src)
                    
                    # --- CARA VUELTA / REVERSO (Impresión Par) ---
                    page_back = doc_out.new_page(width=w_pt, height=h_pt)
                    
                    if not is_rtl: # LTR Occidental
                        left_src = sig_start + (2 * i + 1)
                        right_src = sig_start + (sig_size - 2 * i - 2)
                    else:          # RTL Manga
                        left_src = sig_start + (sig_size - 2 * i - 2)
                        right_src = sig_start + (2 * i + 1)
                        
                    page_back.show_pdf_page(rect_left, doc_temp, left_src)
                    page_back.show_pdf_page(rect_right, doc_temp, right_src)
                    
                # UI Progress
                self.progress["value"] = int(((sig_idx + 1) / num_signatures) * 100)
                self.root.update_idletasks()
            
            # Guardar el documento optimizado
            doc_out.save(out_p, garbage=4, deflate=True)
            doc_out.close()
            if in_p.lower().endswith('.cbz') or True:
                doc_temp.close()
                
            messagebox.showinfo("Éxito", f"¡PDF Impuesto generado!\nListo para imprimir a doble cara en hojas Carta.\nGuardado en: {out_p}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo en la imposición: {str(e)}")
        finally:
            self.btn_process.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MangaImpositionApp(root)
    root.mainloop()