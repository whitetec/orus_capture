# Orus Capture v1 - by WhiteTec - Argentina (Enero 2025)

import os
import cv2
import numpy as np
import threading
from tkinter import Tk, Label, Button, filedialog, StringVar, IntVar, Entry, OptionMenu, Checkbutton, Canvas, Scrollbar, Text
from tkinter.ttk import Frame
from datetime import datetime
import pytz
import uuid
import mss
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor
import time
import boto3

# Configuración del bucket S3
BUCKET_NAME = "orus-repo-01"

# Función para generar un ID único
def generate_unique_id():
    return uuid.uuid4().hex[:8]

# Subida a S3
def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Archivo subido exitosamente: {s3_key}")
    except Exception as e:
        print(f"Error al subir {file_path}: {e}")

# Captura de monitor
def capture_monitor(monitor_number):
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_number > len(monitors) or monitor_number < 1:
            raise ValueError("Número de monitor inválido.")
        monitor = monitors[monitor_number]
        screenshot = np.array(sct.grab(monitor))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

# Clase principal de la aplicación
class OrusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Orus Capture")

        # Variables de configuración
        self.node_number = StringVar(value="01")
        self.save_dir = StringVar(value=os.getcwd())
        self.selected_monitor = IntVar(value=1)
        self.upload_to_s3 = IntVar(value=1)
        self.loop_enabled = False
        self.loop_interval = IntVar(value=10)
        self.is_running = threading.Event()

        # Configuración de UI
        self.setup_ui()

    def setup_ui(self):
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuración (Panel Izquierdo)
        config_frame = Frame(frame)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        Label(config_frame, text="Número de Nodo:").grid(row=0, column=0, sticky="w")
        Entry(config_frame, textvariable=self.node_number).grid(row=0, column=1, sticky="ew")

        Label(config_frame, text="Carpeta de Guardado:").grid(row=1, column=0, sticky="w")
        Button(config_frame, text="Seleccionar", command=self.select_folder).grid(row=1, column=1, sticky="ew")
        Label(config_frame, textvariable=self.save_dir, fg="blue").grid(row=2, column=0, columnspan=2, sticky="w")

        Label(config_frame, text="Seleccionar Monitor:").grid(row=3, column=0, sticky="w")
        OptionMenu(config_frame, self.selected_monitor, *[i for i in range(1, len(mss.mss().monitors))]).grid(row=3, column=1, sticky="ew")

        Label(config_frame, text="Intervalo (segundos):").grid(row=4, column=0, sticky="w")
        Entry(config_frame, textvariable=self.loop_interval).grid(row=4, column=1, sticky="ew")

        Button(config_frame, text="Iniciar Captura", command=self.capture_manual).grid(row=5, column=0, pady=10)
        Button(config_frame, text="Activar Bucle", command=self.start_loop).grid(row=6, column=0, pady=10)
        Button(config_frame, text="Detener Bucle", command=self.stop_loop).grid(row=6, column=1, pady=10)
        Button(config_frame, text="Salir", command=self.root.quit).grid(row=7, column=0, columnspan=2, pady=10)

        # Vista Previa (Panel Derecho)
        preview_frame = Frame(frame)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.preview_label = Label(preview_frame, text="Vista previa del monitor seleccionado")
        self.preview_label.pack(fill="both", expand=True)

        # Consola de Estado (Panel Inferior)
        status_frame = Frame(frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        scrollbar = Scrollbar(status_frame)
        scrollbar.pack(side="right", fill="y")

        self.status_console = Text(status_frame, height=10, wrap="word", yscrollcommand=scrollbar.set, state="disabled")
        self.status_console.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.status_console.yview)

        self.update_preview()

    def set_status(self, message, color="black"):
        """Actualiza la consola de estado."""
        self.status_console.config(state="normal")
        self.status_console.insert("end", f"{message}\n")
        self.status_console.tag_add("current_line", "end-2l", "end-1c")
        self.status_console.tag_config("current_line", foreground=color)
        self.status_console.see("end")
        self.status_console.config(state="disabled")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_dir.set(folder)

    def capture_manual(self):
        """Captura única manual."""
        self.set_status("Capturando pantalla...", "blue")
        try:
            screenshot = capture_monitor(self.selected_monitor.get())
            self.save_and_upload(screenshot)
            self.set_status("Captura completada exitosamente.", "green")
        except Exception as e:
            self.set_status(f"Error: {e}", "red")

    def start_loop(self):
        """Inicia el bucle de capturas."""
        if self.loop_enabled:
            return
        self.loop_enabled = True
        self.is_running.set()
        threading.Thread(target=self.run_loop).start()

    def stop_loop(self):
        """Detiene el bucle de capturas."""
        self.loop_enabled = False
        self.is_running.clear()
        self.set_status("Bucle detenido.", "red")

    def run_loop(self):
        """Ejecuta el bucle de capturas."""
        while self.loop_enabled and self.is_running.is_set():
            self.set_status("Capturando pantalla en bucle...", "blue")
            self.capture_manual()
            time.sleep(self.loop_interval.get())

    def save_and_upload(self, screenshot):
        """Guarda la captura y los recortes, y los sube al bucket."""
        try:
            # Zona horaria
            timezone = pytz.timezone("America/Argentina/Buenos_Aires")
            timestamp = datetime.now(timezone).strftime("%Y-%m-%d-%H-%M-%S-GMT-03")

            # Crear carpeta dinámica
            node_name = f"orus-data-node-{int(self.node_number.get()):02d}"
            base_path = os.path.join(self.save_dir.get(), node_name, timestamp)
            os.makedirs(base_path, exist_ok=True)

            # Guardar captura principal
            self.set_status("Guardando captura principal...", "blue")
            unique_id = generate_unique_id()
            main_filename = f"{node_name}_{timestamp}_{unique_id}.png"
            main_path = os.path.join(base_path, main_filename)
            cv2.imwrite(main_path, screenshot)

            # Subir captura principal a S3
            if self.upload_to_s3.get():
                self.set_status("Subiendo captura principal al bucket...", "blue")
                s3_main_key = f"{node_name}/{timestamp}/main/{main_filename}"
                upload_to_s3(main_path, BUCKET_NAME, s3_main_key)

            # Dividir en 3x3 y guardar recortes
            height, width, _ = screenshot.shape
            segment_height, segment_width = height // 3, width // 3

            self.set_status("Generando y subiendo recortes...", "blue")

            recorte_tasks = []
            with ThreadPoolExecutor() as executor:
                for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)], start=1):
                    # Crear carpeta para el segmento
                    stream_folder = os.path.join(base_path, f"stream_{i:03d}")
                    os.makedirs(stream_folder, exist_ok=True)

                    # Generar nombre único para el archivo
                    stream_id = generate_unique_id()
                    stream_filename = f"stream_{i:03d}_{timestamp}_{stream_id}.png"
                    stream_path = os.path.join(stream_folder, stream_filename)

                    # Recortar el segmento
                    left = col * segment_width
                    top = row * segment_height
                    right = left + segment_width
                    bottom = top + segment_height
                    segment = screenshot[top:bottom, left:right]

                    # Guardar el segmento
                    cv2.imwrite(stream_path, segment)

                    # Subir segmento a S3
                    if self.upload_to_s3.get():
                        s3_key = f"{node_name}/{timestamp}/stream_{i:03d}/{stream_filename}"
                        recorte_tasks.append(executor.submit(upload_to_s3, stream_path, BUCKET_NAME, s3_key))

            # Esperar a que todas las subidas terminen
            for task in recorte_tasks:
                task.result()

            self.set_status("Proceso completado. Todos los archivos se han guardado y subido correctamente.", "green")

        except Exception as e:
            self.set_status(f"Error al guardar/subir: {e}", "red")


    def update_preview(self):
        """Actualizar la vista previa del monitor seleccionado."""
        try:
            screenshot = capture_monitor(self.selected_monitor.get())
            image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
        except Exception as e:
            self.preview_label.config(text=f"Error: {e}")
        self.root.after(1000, self.update_preview)

# Inicializar la aplicación
if __name__ == "__main__":
    root = Tk()
    app = OrusApp(root)
    root.mainloop()
