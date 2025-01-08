# ORUS Capture

## Descripción
Aplicación para capturar pantallas, dividirlas en recortes 3x3 y almacenarlas localmente o en un bucket S3 de AWS.

---

## Requisitos

- **Sistema Operativo**: Windows 10 o superior.
- **Python**: 3.12.2+
- Dependencias: `boto3`, `numpy`, `opencv-python`, `mss`, `Pillow`, `pytz`

---

## Instalación

1. Clona el repositorio:

       git clone https://github.com/tu-repositorio/orus-capture.git
       cd orus-capture

Instala las dependencias:

    pip install -r requirements.txt

Configura AWS CLI:

    aws configure


## Ejecución

Ejecuta la aplicación con:

    python orus_capture_ui.py



Configura las opciones en la interfaz gráfica y comienza a capturar.
