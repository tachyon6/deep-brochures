# Gunicorn configuration file for production
import os
import signal
import subprocess

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 1  # EC2 t3.micro에서는 1개 워커 권장
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "media_kit_api"

# Worker tmp directory
worker_tmp_dir = "/dev/shm"

# Preload app for memory efficiency
preload_app = True

def on_starting(server):
    """Hook called before starting workers"""
    port = 8000
    print(f"🧹 Cleaning up existing processes on port {port}...")
    
    try:
        # Find processes using port 8000
        result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found existing process(es) on port {port}: {', '.join(pids)}")
            
            # Kill existing processes
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Sent TERM signal to process {pid}")
                except (ProcessLookupError, ValueError):
                    pass
            
            # Wait a bit for graceful shutdown
            import time
            time.sleep(2)
            
            # Force kill if still running
            result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                remaining_pids = result.stdout.strip().split('\n')
                for pid in remaining_pids:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"Force killed stubborn process {pid}")
                    except (ProcessLookupError, ValueError):
                        pass
            
            print(f"✅ Port {port} cleaned up")
        else:
            print(f"✅ Port {port} is already free")
            
    except FileNotFoundError:
        print("⚠️ lsof command not found, skipping port cleanup")
    except Exception as e:
        print(f"⚠️ Error during port cleanup: {e}")
    
    print("🌟 Starting gunicorn server...")

def on_exit(server):
    """Hook called when server exits"""
    print("👋 Server shutting down...") 