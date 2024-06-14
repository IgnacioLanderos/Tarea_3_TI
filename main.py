import requests
import schedule
import time
from subprocess import run

def download_from_bucket():
    # Ejecutar el script download_files.py
    run(["python", "scripts/download_files.py"])

def process_data_and_update_dashboard():
    # Ejecutar el script process_data.py
    run(["python", "scripts/process_data.py"])

    # Llamar a la función main() del dashboard después del procesamiento
    import scripts.dashboard
    scripts.dashboard.main()

def schedule_download_process_and_dashboard_update():
    # Programar la descarga desde el bucket
    schedule.every().day.at("08:00").do(download_from_bucket)
    schedule.every().day.at("20:00").do(download_from_bucket)

    # Programar el procesamiento de datos y actualización del dashboard después de la descarga
    schedule.every().day.at("08:30").do(process_data_and_update_dashboard)
    schedule.every().day.at("20:30").do(process_data_and_update_dashboard)

    # Ejecutar la programación de tareas
    while True:
        schedule.run_pending()
        time.sleep(60)  # Esperar 60 segundos antes de verificar de nuevo

if __name__ == "__main__":
    schedule_download_process_and_dashboard_update()
