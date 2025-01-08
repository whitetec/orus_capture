# Orus Capture v1 - by WhiteTec - Argentina (Enero 2025)

import os
import cv2
import numpy as np
import boto3
from tkinter import Tk, Label, Button, filedialog, messagebox, simpledialog
from datetime import datetime
import pytz
import uuid
import mss

# Configuración del bucket S3
BUCKET_NAME = "orus-repo-01"

def generate_unique_id():
    """Genera un ID único de 8 caracteres alfanuméricos en minúsculas."""
    return uuid.uuid4().hex[:8]

def upload_to_s3(file_path, bucket_name, s3_key):
    """Sube un archivo al bucket S3."""
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Archivo subido exitosamente: {s3_key}")
    except Exception as e:
        print(f"Error al subir {file_path}: {e}")

def capture_monitor(monitor_number):
    """Captura la pantalla del monitor seleccionado usando MSS."""
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_number > len(monitors) or monitor_number < 1:
            raise ValueError("Número de monitor inválido.")
        monitor = monitors[monitor_number]
        screenshot = np.array(sct.grab(monitor))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

def process_capture(save_dir, monitor_number, node_number, upload_to_s3_enabled):
    """Captura la pantalla del monitor seleccionado, procesa y sube a S3."""
    # Obtener la zona horaria de Buenos Aires
    timezone = pytz.timezone("America/Argentina/Buenos_Aires")
    timestamp = datetime.now(timezone).strftime("%Y-%m-%d-%H-%M-%S-GMT-03")

    # Crear nodo dinámico
    node_name = f"orus-data-node-{node_number:02d}"

    # Capturar el monitor seleccionado
    try:
        screenshot = capture_monitor(monitor_number)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo capturar el monitor {monitor_number}: {e}")
        return

    height, width, _ = screenshot.shape
    print(f"Tamaño de la captura: {width}x{height}")

    # Crear carpetas dinámicas
    base_path = os.path.join(save_dir, node_name, timestamp)
    main_folder = os.path.join(base_path, "main")
    os.makedirs(main_folder, exist_ok=True)

    # Guardar la captura principal
    unique_id = generate_unique_id()
    main_filename = f"{node_name}_{timestamp}_{unique_id}.png"
    main_path = os.path.join(main_folder, main_filename)
    cv2.imwrite(main_path, screenshot)
    print(f"Captura principal guardada en: {main_path}")

    # Subir captura principal a S3
    if upload_to_s3_enabled:
        s3_main_key = f"{node_name}/{timestamp}/main/{main_filename}"
        upload_to_s3(main_path, BUCKET_NAME, s3_main_key)

    # Dividir en 3x3 y guardar segmentos
    segment_height, segment_width = screenshot.shape[0] // 3, screenshot.shape[1] // 3
    for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)], start=1):
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

        # Guardar el recorte
        cv2.imwrite(stream_path, segment)
        print(f"Segmento guardado en: {stream_path}")

        # Subir segmento a S3
        if upload_to_s3_enabled:
            s3_key = f"{node_name}/{timestamp}/stream_{i:03d}/{stream_filename}"
            upload_to_s3(stream_path, BUCKET_NAME, s3_key)

    messagebox.showinfo("Éxito", "Proceso completado exitosamente.")

def start_capture():
    """Inicia la captura con opciones personalizadas."""
    root = Tk()
    root.withdraw()

    # Solicitar el número de nodo
    node_number = simpledialog.askinteger(
        "Número de Nodo",
        "Ingresa el número del nodo (solo números):",
        minvalue=1,
        maxvalue=99,
    )
    if not node_number:
        messagebox.showerror("Error", "Debe ingresar un número de nodo válido.")
        return

    # Seleccionar carpeta
    save_dir = filedialog.askdirectory(title="Selecciona la carpeta para guardar las imágenes")
    if not save_dir:
        messagebox.showerror("Error", "Por favor selecciona una carpeta.")
        return

    # Seleccionar monitor
    with mss.mss() as sct:
        monitors = sct.monitors
        monitor_options = [f"Monitor {i}" for i in range(1, len(monitors))]
        monitor_number = simpledialog.askinteger(
            "Seleccionar monitor",
            f"Hay {len(monitors) - 1} monitores disponibles.\nSelecciona un monitor (1-{len(monitors) - 1}):",
            minvalue=1,
            maxvalue=len(monitors) - 1,
        )
        if not monitor_number:
            messagebox.showerror("Error", "Debe seleccionar un monitor válido.")
            return

    # Confirmar si se desea subir a S3
    upload_to_s3_enabled = messagebox.askyesno("Subir a AWS S3", "¿Deseas subir las capturas al bucket S3?")

    # Procesar captura
    process_capture(save_dir, monitor_number, node_number, upload_to_s3_enabled)

if __name__ == "__main__":
    start_capture()
