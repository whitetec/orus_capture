# orus_capture
Python Capture &amp; Storage for web videowalls.
ORUS Capture v1

Descripción
ORUS Capture es una aplicación diseñada para capturar pantallas de monitores seleccionados, dividir las capturas en recortes de 3x3, y almacenar las imágenes localmente y en un bucket S3 de AWS. Incluye una interfaz gráfica amigable que permite configurar las opciones y realizar capturas de forma manual o automática en bucle.
Requisitos del sistema

    Sistema Operativo: Windows 10 o superior.
    Python: Versión 3.12.2 o superior.
    Dependencias adicionales:
        boto3
        numpy
        opencv-python
        mss
        Pillow
        pytz
        tkinter (viene incluido con Python)

Instrucciones de Instalación

    Clona o descarga este repositorio

git clone https://github.com/tu-repositorio/orus-capture.git
cd orus-capture

Instala Python 3.12.2
Descarga Python desde python.org y asegúrate de agregar Python al PATH durante la instalación.

Instala las dependencias necesarias Abre una terminal en la carpeta del proyecto y ejecuta:

pip install -r requirements.txt

Si no tienes un archivo requirements.txt, crea uno con este contenido:

boto3
numpy
opencv-python
mss
Pillow
pytz

Configura AWS CLI La aplicación utiliza AWS para subir capturas al bucket S3. Asegúrate de que AWS CLI esté configurado:

    Instala AWS CLI: Guía de instalación
    Configura las credenciales:

    aws configure

    Proporciona tu Access Key ID, Secret Access Key, región y formato de salida (por ejemplo, json).

Verifica la conexión con tu bucket S3 Ejecuta este comando para asegurarte de que tu bucket es accesible:

    aws s3 ls

Cómo usar la aplicación

    Ejecuta la aplicación En la carpeta donde está el archivo orus_capture_ui.py, abre una terminal y ejecuta:

python orus_capture_ui.py

Configura las opciones

    Número de Nodo: Define el nodo de trabajo (por ejemplo, 01).
    Carpeta de Guardado: Selecciona la carpeta donde se guardarán las capturas localmente.
    Seleccionar Monitor: Elige el monitor que deseas capturar.
    Modo Bucle: Activa/desactiva el modo de captura automática en intervalos definidos.
    Intervalo (segundos): Define el tiempo entre capturas en el modo bucle.

Inicia la captura

    Manual: Haz clic en "Iniciar Captura" para realizar una captura única.
    Automático: Activa el "Modo Bucle" y ajusta el intervalo antes de iniciar la captura.

Detén el bucle (si está activo) Haz clic en "Detener Bucle" para finalizar la captura automática.

Verifica las subidas Los archivos se guardarán en el bucket S3 especificado. Puedes verificar los archivos usando:

    aws s3 ls s3://<nombre-del-bucket> --recursive

Estructura del Proyecto

ORUS_APP_CAPTURE/
├── capturas/                # Carpeta de guardado local
├── orus_capture_ui.py       # Código principal con la interfaz gráfica
├── orus_capture.py          # Código auxiliar (si es necesario separarlo)
├── README.md                # Este archivo
└── requirements.txt         # Dependencias necesarias

Notas

    Zona Horaria: Las capturas incluyen un timestamp basado en la hora de Buenos Aires (GMT-03).
    Estructura en S3:

    <bucket-name>/<orus-data-node-XX>/<timestamp>/main/<filename>.png
    <bucket-name>/<orus-data-node-XX>/<timestamp>/stream_YYY/<filename>.png

Posibles Problemas y Soluciones

    Error: "AWS Access Key ID does not exist"
        Verifica que has configurado correctamente AWS CLI con las credenciales válidas.

    No se generan recortes
        Asegúrate de que la captura principal sea válida y tenga una resolución compatible (1920x1080).

    El programa no responde
        Verifica que el modo bucle no esté configurado con un intervalo demasiado bajo (<10 segundos).

    El archivo orus_capture_ui.py no se ejecuta
        Asegúrate de estar usando la versión de Python correcta (python --version).
        Verifica que las dependencias estén instaladas (pip list).
