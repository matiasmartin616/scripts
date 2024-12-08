import os
import fnmatch
from concurrent.futures import ThreadPoolExecutor

# Diccionario de nombres de archivos comunes
file_dict = [
    "config.php",
    "db_credentials.txt",
    "backup.zip",
    ".env",
    "settings.py",
    "id_rsa",
    "id_rsa.pub",
    "private.key",
    "secret.key",
]

# Cadenas de texto comunes para búsqueda dentro de archivos
text_dict = [
    "password",
    "secret",
    "PRIVATE KEY",
    "API_KEY",
    "db_user",
    "db_password",
]

# Función para buscar archivos por nombre
def find_files_by_name(root_dir, file_dict):
    found_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for pattern in file_dict:
            for filename in fnmatch.filter(filenames, pattern):
                full_path = os.path.join(dirpath, filename)
                found_files.append(full_path)
    return found_files

# Función para buscar texto dentro de archivos
def search_text_in_files(file_path, text_dict):
    try:
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()
            matches = [text for text in text_dict if text in content]
            if matches:
                return file_path, matches
    except (PermissionError, IsADirectoryError):
        pass
    return None

# Función principal para enumeración
def enumerate_sensitive_files(root_dir):
    print(f"[+] Iniciando enumeración en: {root_dir}")

    # Paso 1: Buscar archivos por nombre
    print("[+] Buscando archivos sensibles...")
    found_files = find_files_by_name(root_dir, file_dict)
    print(f"[+] Archivos encontrados: {len(found_files)}")
    
    # Paso 2: Buscar texto en archivos encontrados
    print("[+] Buscando coincidencias de texto dentro de archivos...")
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(search_text_in_files, file, text_dict) for file in found_files]
        for future in futures:
            result = future.result()
            if result:
                results.append(result)

    # Salida
    print("[+] Enumeración completada.")
    for file_path, matches in results:
        print(f"[!] Coincidencias encontradas en {file_path}: {', '.join(matches)}")

if __name__ == "__main__":
    # Ruta inicial para enumeración
    root_directory = input("Ingrese la ruta para buscar (e.g., '/var/www' o 'C:/Users'): ").strip()
    enumerate_sensitive_files(root_directory)