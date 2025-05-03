import requests
from bs4 import BeautifulSoup
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os

ctk.set_default_color_theme("blue")

resultados = []
archivo_guardado = None  # Ruta del último archivo guardado

def scrape():
    global resultados
    url = url_entry.get()
    tags = tag_entry.get()
    filtro = filtro_entry.get().strip().lower()

    if not url or not tags:
        messagebox.showwarning("Campos vacíos", "Por favor, ingresa una URL y etiquetas.")
        return

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        resultados.clear()
        output_text.configure(state="normal")
        output_text.delete("1.0", "end")

        for tag in tag_list:
            elementos = soup.find_all(tag)
            for i, elemento in enumerate(elementos, start=1):
                texto = elemento.get_text(strip=True)
                if texto and (not filtro or filtro in texto.lower()):
                    resultados.append((tag, texto))
                    output_text.insert("end", f"<{tag}> {texto}\n\n")

        output_text.configure(state="disabled")

        if not resultados:
            messagebox.showinfo("Sin resultados", f"No se encontraron elementos que cumplan con los criterios.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

def exportar():
    global archivo_guardado
    if not resultados:
        messagebox.showwarning("Nada que exportar", "Primero realiza una extracción.")
        return

    archivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")],
        title="Guardar como"
    )
    if archivo:
        try:
            if archivo.endswith(".csv"):
                df = pd.DataFrame(resultados, columns=["Etiqueta", "Contenido extraído"])
                df.to_csv(archivo, index=False, encoding="utf-8-sig")
            else:
                with open(archivo, "w", encoding="utf-8") as f:
                    for etiqueta, texto in resultados:
                        f.write(f"<{etiqueta}> {texto}\n\n")
            archivo_guardado = archivo
            preview_button.configure(state="normal")
            messagebox.showinfo("Éxito", f"Datos exportados a:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def previsualizar():
    if archivo_guardado and os.path.exists(archivo_guardado):
        vista = ctk.CTkToplevel()
        vista.title("Previsualización del archivo")
        vista.geometry("700x500")
        
        texto_vista = ctk.CTkTextbox(vista, wrap="word", width=650, height=450)
        texto_vista.pack(padx=20, pady=20)

        with open(archivo_guardado, "r", encoding="utf-8") as f:
            contenido = f.read()
            texto_vista.insert("1.0", contenido)
            texto_vista.configure(state="disabled")
    else:
        messagebox.showwarning("Archivo no encontrado", "No se puede acceder al archivo exportado.")

def cambiar_modo(opcion):
    ctk.set_appearance_mode(opcion)

# GUI
app = ctk.CTk()
app.title("Web Scraper Moderno")
app.geometry("850x750")

frame = ctk.CTkFrame(app, corner_radius=10)
frame.pack(pady=20, padx=20, fill="x")

# Selector de tema
theme_label = ctk.CTkLabel(frame, text="Modo:")
theme_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
theme_selector = ctk.CTkOptionMenu(frame, values=["System", "Light", "Dark"], command=cambiar_modo)
theme_selector.set("System")
theme_selector.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Entrada de URL
url_label = ctk.CTkLabel(frame, text="URL:")
url_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
url_entry = ctk.CTkEntry(frame, width=600)
url_entry.grid(row=1, column=1, pady=5, padx=10)

# Entrada de etiquetas
tag_label = ctk.CTkLabel(frame, text="Etiquetas (separadas por coma):")
tag_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
tag_entry = ctk.CTkEntry(frame, width=400)
tag_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)

# Entrada de filtro
filtro_label = ctk.CTkLabel(frame, text="Filtro (opcional):")
filtro_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
filtro_entry = ctk.CTkEntry(frame, width=400)
filtro_entry.grid(row=3, column=1, sticky="w", pady=5, padx=10)

# Botones
button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=10)

scrape_button = ctk.CTkButton(button_frame, text="Extraer", command=scrape)
scrape_button.pack(side="left", padx=10)

export_button = ctk.CTkButton(button_frame, text="Exportar (CSV o TXT)", command=exportar)
export_button.pack(side="left", padx=10)

preview_button = ctk.CTkButton(button_frame, text="Previsualizar", command=previsualizar, state="disabled")
preview_button.pack(side="left", padx=10)

# Área de texto
output_text = ctk.CTkTextbox(app, width=800, height=400, wrap="word", state="disabled")
output_text.pack(padx=20, pady=10)

app.mainloop()
