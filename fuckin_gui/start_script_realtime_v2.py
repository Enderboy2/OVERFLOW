import subprocess
import re
import logging
import time
import signal

# Configure logging
logging.basicConfig(filename='camera_stream.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

processes = {}

def list_cameras():
    try:
        result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        cameras = []
        current_camera = None
        
        for line in output.split("\n"):
            line = line.strip()
            
            if not line:
                continue
            
            if ":" in line:  # Camera name line
                if current_camera:
                    cameras.append(current_camera)
                current_camera = {"name": line[:-1], "devices": []}
            elif current_camera:
                match = re.search(r"/dev/video\d+", line)
                if match:
                    current_camera["devices"].append(match.group())
        
        if current_camera:
            cameras.append(current_camera)
        
        return cameras
    except subprocess.CalledProcessError as e:
        logging.error("Failed to list cameras: %s", e.stderr)
        return []

def start_camera_stream(idx, cam):
    if cam["devices"]:
        last_device = cam["devices"][-1]
        port = 8080 + idx
        command = [
            "./mjpg_streamer",
            "-i", f"input_uvc.so -d {last_device} -r 352x288",
            "-o", f"output_http.so -p {port} -w ./www"
        ]
        logging.info(f"Starting stream for {cam['name']} on {last_device} at port {port}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes[port] = process
        return process

def monitor_processes():
    while True:
        for port, process in list(processes.items()):
            if process.poll() is not None:  # Process has stopped
                logging.error(f"Stream on port {port} crashed. Restarting...")
                cameras = list_cameras()
                for idx, cam in enumerate(cameras):
                    if 8080 + idx == port:
                        processes[port] = start_camera_stream(idx, cam)
        time.sleep(5)

def stop_camera_stream(port):
    if port in processes:
        processes[port].terminate()
        logging.info(f"Stopped stream on port {port}")
        del processes[port]

def restart_camera_stream(port):
    stop_camera_stream(port)
    time.sleep(2)
    cameras = list_cameras()
    for idx, cam in enumerate(cameras):
        if 8080 + idx == port:
            start_camera_stream(idx, cam)

def cleanup_on_exit(signum, frame):
    logging.info("Stopping all camera streams...")
    for port in list(processes.keys()):
        stop_camera_stream(port)
    exit(0)

def cli_interface():
    while True:
        command = input("Enter command (list, stop [port], restart [port], status, exit): ").strip()
        if command == "list":
            cameras = list_cameras()
            for idx, cam in enumerate(cameras):
                print(f"Camera: {cam['name']}, Port: {8080 + idx}, Devices: {', '.join(cam['devices'])}")
        elif command.startswith("stop "):
            try:
                port = int(command.split()[1])
                stop_camera_stream(port)
            except ValueError:
                print("Invalid port number.")
        elif command.startswith("restart "):
            try:
                port = int(command.split()[1])
                restart_camera_stream(port)
            except ValueError:
                print("Invalid port number.")
        elif command == "status":
            for port, process in processes.items():
                status = "Running" if process.poll() is None else "Stopped"
                print(f"Port {port}: {status}")
        elif command == "exit":
            cleanup_on_exit(None, None)
        else:
            print("Unknown command")

def run_command_for_cameras():
    cameras = list_cameras()
    for idx, cam in enumerate(cameras):
        processes[8080 + idx] = start_camera_stream(idx, cam)
    cli_interface()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)
    run_command_for_cameras()
