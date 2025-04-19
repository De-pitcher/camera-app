import logging, socket, time, os
import psutil

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def find_available_port(start_port, host):
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                s.close()
                return port
        except OSError as e:
            logging.warning(f"Port {port} is in use: {e}. Trying next port.")
            port += 1

def monitor_parent_process():
    """Shut down server if parent process exits."""
    try:
        parent = psutil.Process(os.getppid())
        while True:
            if not parent.is_running():
                logging.info("Parent process exited. Shutting down server...")
                os._exit(0)
            time.sleep(5)
    except Exception as e:
        logging.error(f"Parent monitoring failed: {e}")