# import logging, socket, time, os
# import psutil

# def get_host_ip():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         ip = s.getsockname()[0]
#         s.close()
#         return ip
#     except Exception:
#         return "127.0.0.1"

# def find_available_port(start_port, host):
#     port = start_port
#     while True:
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.bind((host, port))
#                 s.close()
#                 return port
#         except OSError as e:
#             logging.warning(f"Port {port} is in use: {e}. Trying next port.")
#             port += 1

# def monitor_parent_process():
#     """Shut down server if parent process exits."""
#     try:
#         parent = psutil.Process(os.getppid())
#         while True:
#             if not parent.is_running():
#                 logging.info("Parent process exited. Shutting down server...")
#                 os._exit(0)
#             time.sleep(5)
#     except Exception as e:
#         logging.error(f"Parent monitoring failed: {e}")

import logging
import socket
import time
import os
import psutil


def get_host_ip():
    """Attempts to get the local IP address by connecting to a public DNS server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        logging.info(f"Resolved host IP: {ip}")
        return ip
    except Exception as e:
        logging.warning(f"Could not resolve host IP. Defaulting to 127.0.0.1. Error: {e}")
        return "127.0.0.1"


def find_available_port(start_port, host):
    """Finds an available TCP port starting from `start_port` on the given `host`."""
    port = start_port
    while port < 65535:  # Avoid infinite loops
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                logging.info(f"Found available port: {port}")
                return port
        except OSError as e:
            logging.warning(f"Port {port} is in use or unavailable: {e}. Trying next port.")
            port += 1
    raise RuntimeError("No available ports found in range.")


def monitor_parent_process():
    """Terminates the server if the parent process exits."""
    try:
        parent_pid = os.getppid()
        parent = psutil.Process(parent_pid)
        logging.info(f"Monitoring parent process (PID: {parent_pid})...")

        while True:
            if not parent.is_running():
                logging.info("Parent process exited. Shutting down server...")
                os._exit(0)

            # Optional: check if process status is 'zombie' or 'dead'
            if parent.status() in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                logging.info("Parent process is a zombie or dead. Exiting.")
                os._exit(0)

            time.sleep(5)

    except psutil.NoSuchProcess:
        logging.warning("Parent process no longer exists. Shutting down.")
        os._exit(0)
    except Exception as e:
        logging.error(f"Error while monitoring parent process: {e}")
