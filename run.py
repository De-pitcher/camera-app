# import argparse
# import threading
# import sys
# import logging
# import signal

# from waitress import serve
# from app import create_app
# from app.utils import get_host_ip, monitor_parent_process
# from app.logging_config import setup_logging
# from app.routes import executor  # Import the shared ThreadPoolExecutor

# should_exit = threading.Event()

# def parse_args():
#     parser = argparse.ArgumentParser(description="Start the Flask camera server.")
#     parser.add_argument("--host", type=str, help="Host to run on", default=None)
#     parser.add_argument("--port", type=int, help="Port to run on", default=5000)
#     return parser.parse_args()

# def shutdown_gracefully(signum, frame):
#     logging.info("🛑 Received shutdown signal. Cleaning up...")
#     should_exit.set()
#     executor.shutdown(wait=False, cancel_futures=True)
#     sys.exit(0)

# def main():
#     args = parse_args()

#     setup_logging()
#     logger = logging.getLogger(__name__)

#     host = args.host or get_host_ip()
#     port = args.port

#     logger.info(f"🚀 Starting server on http://{host}:{port}")
#     app = create_app()

#     # Handle signals
#     signal.signal(signal.SIGINT, shutdown_gracefully)
#     signal.signal(signal.SIGTERM, shutdown_gracefully)

#     # Start parent monitor in background
#     threading.Thread(target=monitor_parent_process, daemon=True).start()

#     try:
#         serve(app, host=host, port=port)
#     except Exception as e:
#         logger.error(f"💥 Error starting server: {e}")
#         executor.shutdown(wait=False, cancel_futures=True)
#         sys.exit(1)

# if __name__ == "__main__":
#     main()
import argparse
import threading
import os
import sys
import atexit
import msvcrt
import psutil
import logging
from app import create_app
from app.utils import get_host_ip, monitor_parent_process
from app.logging_config import setup_logging
from waitress import serve
from pathlib import Path

# Set lock file in a writable user directory
if sys.platform == "win32":
    base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
else:
    base_dir = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

lock_dir = os.path.join(base_dir, "ClockInApp")
os.makedirs(lock_dir, exist_ok=True)

LOCKFILE = os.path.join(lock_dir, "flask_camera_server.lock")
lockfile_handle = None  # Global lockfile handle


def acquire_lock():
    global lockfile_handle
    try:
        lockfile_handle = open(LOCKFILE, 'w+')
        msvcrt.locking(lockfile_handle.fileno(), msvcrt.LK_NBLCK, 1)

        try:
            lockfile_handle.seek(0)
            pid_str = lockfile_handle.read().strip()
            if pid_str:
                pid = int(pid_str)
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait()
                    logging.info(f"Terminated old process with PID {pid}")
                except psutil.NoSuchProcess:
                    pass
        except Exception:
            pass

        lockfile_handle.seek(0)
        lockfile_handle.truncate()
        lockfile_handle.write(str(os.getpid()))
        lockfile_handle.flush()
    except OSError:
        print("❌ Another instance is already running.")
        sys.exit(1)


def release_lock():
    global lockfile_handle
    if lockfile_handle:
        try:
            msvcrt.locking(lockfile_handle.fileno(), msvcrt.LK_UNLCK, 1)
            lockfile_handle.close()
            os.remove(LOCKFILE)
        except Exception as e:
            print(f"⚠️ Failed to release lock: {e}")


atexit.register(release_lock)


def parse_args():
    parser = argparse.ArgumentParser(description="Start the Flask camera server.")
    parser.add_argument("--host", type=str, help="Host to run on", default=None)
    parser.add_argument("--port", type=int, help="Port to run on", default=5000)
    return parser.parse_args()


def main():
    acquire_lock()

    setup_logging()
    logger = logging.getLogger(__name__)

    args = parse_args()
    host = args.host or get_host_ip()
    port = args.port

    logger.info(f"Starting server on http://{host}:{port}")
    app = create_app()

    threading.Thread(target=monitor_parent_process, daemon=True).start()

    try:
        serve(app, host=host, port=port)
    except KeyboardInterrupt:
        print("Shutting down via KeyboardInterrupt")
        from app.camera import shutdown_server
        shutdown_server()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
