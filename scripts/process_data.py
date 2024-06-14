import os
import csv
import json
import logging
from datetime import datetime
import pandas as pd

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_process_data():
    # Obtén la ruta del directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ruta al directorio donde se encuentran los archivos orders.csv
    orders_dir = os.path.join(current_dir, '..', 'downloads', 'orders')

    # Lista para almacenar todos los datos de órdenes
    all_orders = []

    # Procesar los archivos orders.csv en cada subdirectorio de orders
    for subdir, _, files in os.walk(orders_dir):
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(subdir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f, delimiter=';')
                        for row in reader:
                            # Convertir la fecha a un formato estándar si es necesario
                            if 'timestamp' in row:
                                row['timestamp'] = format_date(row['timestamp'])
                            all_orders.append(row)
                except FileNotFoundError:
                    logger.error(f"No se encontró el archivo {file_path}.")
                except Exception as e:
                    logger.error(f"Error al procesar {file_path}: {str(e)}")

    # Escribir los datos de órdenes en un archivo CSV
    orders_csv_file = os.path.join(current_dir, 'all_orders.csv')
    write_to_csv(all_orders, orders_csv_file)

    # Ruta al directorio donde se encuentran los archivos records.json
    products_dir = os.path.join(current_dir, '..', 'downloads', 'products')

    # Lista para almacenar todos los datos de productos
    all_products = []

    # Procesar los archivos records.json en cada subdirectory de products
    for subdir, _, files in os.walk(products_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(subdir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Añadir cada registro a la lista
                        all_products.extend(data)
                except FileNotFoundError:
                    logger.error(f"No se encontró el archivo {file_path}.")
                except json.JSONDecodeError as e:
                    logger.error(f"Error al decodificar JSON en {file_path}: {str(e)}")

    # Eliminar duplicados basados en objectID en all_products
    all_products_unique = []
    seen_object_ids = set()
    for product in all_products:
        object_id = product['objectID']
        if object_id not in seen_object_ids:
            all_products_unique.append(product)
            seen_object_ids.add(object_id)

    # Escribir los datos de productos únicos en un archivo CSV
    products_csv_file = os.path.join(current_dir, 'all_products.csv')
    write_to_csv(all_products_unique, products_csv_file)

    # Crear un conjunto de objectID válidos
    valid_product_ids = set(df['objectID'] for df in pd.read_csv(products_csv_file, chunksize=10000) for index, df in df.iterrows())

    # Filtrar las órdenes para mantener solo las que tienen un product_id válido según objectID
    all_orders_filtered = [order for order in all_orders if order['product_id'] in valid_product_ids]

    # Sobrescribir el archivo CSV de órdenes con las órdenes filtradas
    write_to_csv(all_orders_filtered, orders_csv_file)
    
    # Cargar all_orders.csv y all_products.csv como DataFrames
    orders_df = pd.read_csv(orders_csv_file)
    products_df = pd.read_csv(products_csv_file)
    
    # Corregir el estado de las órdenes
    orders_df['order_status'] = orders_df['order_status'].replace('dereviled', 'delivered')
    
    # Realizar un cruce entre orders_df y products_df usando product_id y objectID
    merged_df = pd.merge(orders_df, products_df, left_on='product_id', right_on='objectID', how='inner')
    
    # Guardar el resultado en un nuevo archivo CSV
    merged_csv_file = os.path.join(current_dir, 'orders_with_products.csv')
    merged_df.to_csv(merged_csv_file, index=False, encoding='utf-8')
    
    logger.info(f'Se ha creado el archivo {merged_csv_file} correctamente.')

def format_date(timestamp):
    # Función para formatear la fecha y hora
    try:
        dt = datetime.strptime(timestamp, '%d-%m-%Y %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return timestamp  # Devolver el mismo valor si no se puede convertir

def write_to_csv(data, csv_file):
    # Obtener los nombres de las columnas a partir de todos los registros
    if data:
        # Usamos un conjunto para asegurarnos de obtener todas las claves únicas
        fieldnames = set().union(*(d.keys() for d in data))
    else:
        fieldnames = []

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    load_and_process_data()