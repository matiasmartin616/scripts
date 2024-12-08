import os
import platform
import subprocess
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

# Función para hacer ping a un host
def ping_host(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]
    try:
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, universal_newlines=True)
        if "ttl" in output.lower():  # Indicación de respuesta válida
            return str(ip)
    except subprocess.CalledProcessError:
        pass
    return None

# Función para obtener direcciones MAC mediante ARP
def get_mac(ip):
    try:
        if platform.system().lower() == "windows":
            output = subprocess.check_output(["arp", "-a", ip], stderr=subprocess.DEVNULL, universal_newlines=True)
        else:
            output = subprocess.check_output(["arp", "-n", ip], stderr=subprocess.DEVNULL, universal_newlines=True)
        for line in output.split("\n"):
            if ip in line:
                return line.split()[1] if platform.system().lower() == "windows" else line.split()[2]
    except Exception:
        pass
    return "No MAC found"

# Función principal de enumeración
def enumerate_network(network):
    print(f"[+] Iniciando enumeración en la red: {network}")
    alive_hosts = []

    #Descubrir hosts activos
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(ping_host, ip) for ip in ipaddress.IPv4Network(network, strict=False)]
        alive_hosts = [host for host in [future.result() for future in futures] if host]

    print(f"[+] Hosts activos encontrados: {len(alive_hosts)}")
    for host in alive_hosts:
        print(f"[+] {host} - Resolviendo MAC...")
        mac = get_mac(host)
        print(f"    [!] Dirección MAC: {mac}")

if __name__ == "__main__":
    # Solicitar rango de red al usuario
    network_range = input("Ingrese el rango de red (e.g., 192.168.1.0/24): ").strip()
    enumerate_network(network_range)