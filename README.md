# Manga & Comic Imposition Tool 📚🎨

Una herramienta de escritorio desarrollada en Python diseñada específicamente para mangakas, creadores de cómics y entusiastas de la autoedición. Este software automatiza el complejo proceso de **imposición de páginas** (*imposition*), transformando archivos secuenciales ordinarios (`.cbz` o `.pdf`) en archivos listos para imprenta en formato de **cuadernillos (signatures)**.

Ideal para preparar tomos para encuadernación rústica pegada (fresada / *perfect binding*) directamente en impresoras domésticas o de taller usando papel estándar (Carta o A4).

---

## ✨ Características Principales

* **Soporte de Formatos:** Lee archivos comprimidos de imágenes (`.cbz`) y documentos (`.pdf`).
* **Imposición Automática por Cuadernillos:** Divide el libro de forma inteligente en pliegos de 16 o 32 páginas (o folleto único) para facilitar el doblado y optimizar el lomo.
* **Control del Sentido de Lectura:** Soporta maquetación tradicional japonesa (**Manga / RTL**) y occidental (**Cómic-Libro / LTR**).
* **Gestión del Margen de Lomo (Gutter):** Permite configurar un espacio en blanco milimétrico en el centro del pliego para que el pegamento no tape el arte ni los diálogos.
* **Procesamiento Vectorial Sin Pérdida:** Al procesar PDFs de origen, utiliza clonación de elementos nativos en lugar de rasterizar, manteniendo la máxima nitidez tipográfica y de línea.
* **Interfaz Gráfica (GUI):** Construida de forma ligera y nativa sobre Tkinter, visualmente limpia y con barra de progreso en tiempo real.

---

## 🚀 Requisitos e Instalación

El script utiliza **PyMuPDF (fitz)** por su increíble rendimiento con archivos pesados y mapas de bits de alta resolución.

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/manga-imposition-tool.git](https://github.com/tu-usuario/manga-imposition-tool.git)
   cd manga-imposition-tool
