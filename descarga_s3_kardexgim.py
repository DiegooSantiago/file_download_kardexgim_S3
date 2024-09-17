import os
import boto3
import tkinter as tk
from tkinter import messagebox
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError, ClientError

# Versión dcruz_240917

def download_files_from_s3(bucket_name, local_directory, aws_access_key_id, aws_secret_access_key):
    """Descarga todos los archivos del bucket de S3 y los guarda en el directorio local."""

    # Crear el cliente de S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # Crear el directorio local si no existe
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Lista para almacenar los nombres de los archivos descargados
    downloaded_files = []

    try:
        # Listar todos los objetos en el bucket
        response = s3.list_objects_v2(Bucket=bucket_name)

        # Verificar si hay contenido en el bucket
        if 'Contents' in response:
            for obj in response['Contents']:
                # Obtener el nombre del archivo y el tamaño
                file_name = obj['Key']
                file_size_bytes = obj['Size']

                # Convertir tamaño de bytes a megabytes
                file_size_mb = file_size_bytes / (1024 * 1024)

                # Definir la ruta completa del archivo local
                local_file_path = os.path.join(local_directory, file_name)

                # Crear subdirectorios si es necesario
                local_subdirectory = os.path.dirname(local_file_path)
                if not os.path.exists(local_subdirectory):
                    os.makedirs(local_subdirectory)

                # Mostrar ventana indicando que se está descargando el archivo
                downloading_window = show_downloading_message(file_size_mb, file_name)

                try:
                    # Descargar el archivo del bucket de S3
                    s3.download_file(bucket_name, file_name, local_file_path)

                    # Cerrar ventana de descarga
                    downloading_window.destroy()

                    downloaded_files.append(file_name)

                except ClientError as e:
                    # Manejo de errores específicos de cliente S3, como permisos insuficientes
                    show_message(f"Error de cliente al descargar {file_name}: {e}", "Error de Descarga")
                    downloading_window.destroy()
                except BotoCoreError as e:
                    # Manejo de errores básicos de Boto3
                    show_message(f"Error de Boto3 al descargar {file_name}: {e}", "Error de Descarga")
                    downloading_window.destroy()
                except Exception as e:
                    # Manejo de otros errores no especificados
                    show_message(f"Error desconocido al descargar {file_name}: {e}", "Error de Descarga")
                    downloading_window.destroy()

            # Mostrar listado de archivos descargados
            show_downloaded_files(downloaded_files, local_directory)
        else:
            show_message("El bucket está vacío o no existe.", "Advertencia")

    except NoCredentialsError:
        show_message("Error: No se encontraron las credenciales de AWS.", "Error de Credenciales")
    except PartialCredentialsError:
        show_message("Error: Las credenciales de AWS están incompletas.", "Error de Credenciales")
    except BotoCoreError as e:
        show_message(f"Error con el servicio de AWS: {e}", "Error")
    except Exception as e:
        show_message(f"Error general al listar los archivos del bucket: {e}", "Error")

def show_message(message, title):
    """Muestra un mensaje en una ventana emergente."""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    messagebox.showinfo(title, message)

def show_downloading_message(file_size_mb, file_name):
    """Muestra una ventana indicando que el archivo está descargándose, junto con su tamaño en MB."""
    root = tk.Tk()
    root.title("Descargando")

    # Configurar el tamaño de la ventana
    window_width = 350
    window_height = 100

    # Obtener el tamaño de la pantalla
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcular la posición centrada
    position_x = int(screen_width / 2 - window_width / 2)
    position_y = int(screen_height / 2 - window_height / 2)

    # Establecer la geometría de la ventana
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Formatear el tamaño del archivo a dos decimales
    file_size_formatted = f"{file_size_mb:.2f} MB"

    # Agregar el texto de descarga
    tk.Label(root, text=f"Descargando {file_size_formatted} - {file_name}...").pack(padx=20, pady=20)

    # Actualizar la ventana para mostrarla inmediatamente
    root.update()

    return root

def show_downloaded_files(files, directory):
    """Muestra una ventana con el listado de archivos descargados y abre el explorador de archivos."""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    if files:
        file_list = "\n".join(files)
        messagebox.showinfo("Archivos Descargados", f"Los siguientes archivos fueron descargados:\n\n{file_list}")
        
        # Abrir el explorador de archivos en la ubicación de descarga
        open_explorer(directory)
    else:
        messagebox.showinfo("Archivos Descargados", "No se descargaron archivos.")

def open_explorer(directory):
    """Abre el explorador de archivos en el directorio especificado."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(directory)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open "{directory}"')  # Comando para macOS
    except Exception as e:
        show_message(f"No se pudo abrir el explorador de archivos: {e}", "Error")

if __name__ == '__main__':
    # Configurar los parámetros según el sistema operativo
    if os.name == 'nt':  # Windows
        local_directory = r'C:\kardexgim'
    elif os.name == 'posix':  # macOS/Linux
        local_directory = os.path.expanduser('~/kardexgim')

    # Nombre del bucket de S3
    bucket_name = 'kardexgim'

    # Credenciales de AWS
    aws_access_key_id = 'AKIAYHVKENECH3NDJWQR'
    aws_secret_access_key = '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'

    # Ejecutar la función para descargar archivos
    download_files_from_s3(bucket_name, local_directory, aws_access_key_id, aws_secret_access_key)
