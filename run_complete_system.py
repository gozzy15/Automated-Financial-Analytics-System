import subprocess
import threading
import time
import sys

def run_streamlit():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "analytics_app.py"
        ]
    )

def run_dash():
    subprocess.run(
        [
            sys.executable,
            "dashboard.py"
        ]
    )

def main():
    print("Starting both dashboards...\n")

    try:

        print("📊 Streamlit Dashboard:")
        print("http://localhost:8501")
        print()
        print("📈 Dash Dashboard:")
        print("http://localhost:8050")
        
        t1 = threading.Thread(
            target=run_streamlit,
            name="StreamlitThread"
        )

        t2 = threading.Thread(
            target=run_dash,
            name="DashThread"
        )
        
        t1.start()
        time.sleep(2)  # Give Streamlit time to start
        t2.start()
        
        t1.join()
        t2.join()

    except KeyboardInterrupt:

        print("\nStopping dashboards...")

    except Exception as exc:

        print(
            f"\nLauncher failed:\n{exc}"
        )

if __name__ == "__main__":
    main()