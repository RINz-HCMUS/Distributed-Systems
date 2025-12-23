import subprocess
import sys
import time
import os
import platform
import glob

def run_all():
    if not os.path.exists('config.json'):
        print("Config not found. Generating...")
        subprocess.run([sys.executable, "generate_config.py"])

    # Dọn dẹp cờ cũ
    if not os.path.exists('flags'): os.makedirs('flags')
    for f in glob.glob("flags/*.done"): os.remove(f)

    print("LAUNCHING SES DISTRIBUTED SYSTEM (15 PROCESSES)...")
    
    processes = []
    base_cmd = [sys.executable, "main.py"]

    # Khởi động và IN PID
    for i in range(1, 16):
        cmd = base_cmd + [str(i)]
        
        if platform.system() == "Windows":
            p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            p = subprocess.Popen(cmd, shell=False)
            
        print(f" -> Starting Process {i:<2} ... [PID: {p.pid}]")
        processes.append(p)
        time.sleep(0.5)

    print(f"\nSuccessfully launched {len(processes)} processes.")
    print("System is running. Watching 'flags/' folder for completion signals...")
    print("(Auto-termination active. Press Ctrl+C to force stop)\n")

    # Vòng lặp giám sát
    try:
        while True:
            time.sleep(1.0)
            
            # Đếm số file cờ
            done_files = glob.glob("flags/*.done")
            count = len(done_files)
            
            # In tiến độ trên cùng 1 dòng
            sys.stdout.write(f"\r >> Status: {count}/15 Processes Finished.")
            sys.stdout.flush()

            if count == 15:
                print("\n\nALL PROCESSES COMPLETED! Terminating system in 3 seconds...")
                time.sleep(3)
                break

    except KeyboardInterrupt:
        print("\nStopping by User request...")

    # Dọn dẹp
    print("Stopping all processes...")
    if platform.system() == "Windows":
         subprocess.run(["taskkill", "/F", "/IM", "python.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        for p in processes: p.terminate()
         
    print("System Stopped.")

if __name__ == "__main__":
    run_all()