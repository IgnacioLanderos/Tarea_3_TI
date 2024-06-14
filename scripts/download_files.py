from google.cloud import storage
import os
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtén la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Obtén la ruta del archivo JSON desde las variables de entorno de Render
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

# Define el nombre del bucket
bucket_name = '2024-1-tarea-3'

def list_blobs(bucket_name):
    """Lista todos los blobs en el bucket."""
    try:
        storage_client = storage.Client.from_service_account_info(credentials_json)
        blobs = storage_client.list_blobs(bucket_name)

        for blob in blobs:
            logger.info(f"Blob: {blob.name}")
            # Define la ruta de destino relativa
            destination_path = os.path.join(current_dir, '..', 'downloads', blob.name)
            download_blob(bucket_name, blob.name, destination_path)
    except Exception as e:
        logger.error(f"Error al listar blobs del bucket {bucket_name}: {str(e)}")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Descarga un blob del bucket."""
    try:
        storage_client = storage.Client.from_service_account_info(credentials_json)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        blob.download_to_filename(destination_file_name)

        logger.info(f"Blob {source_blob_name} descargado a {destination_file_name}.")
    except Exception as e:
        logger.error(f"Error al descargar el blob {source_blob_name}: {str(e)}")

if __name__ == "__main__":
    list_blobs(bucket_name)
