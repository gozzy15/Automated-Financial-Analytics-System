# launch_all.py
import subprocess
import threading
import time
import webbrowser
import sys
import system_initializer


def run_streamlit():
    """Run Streamlit dashboard"""
    print("🚀 Starting Streamlit...")

    subprocess.run([sys.executable, "-m", "streamlit", "run", "analytics_app.py", "--server.port=8501", "--server.headless=true"])
    #subprocess.run(["streamlit", "run", "analytics_app.py", "--server.port=8501", "--server.headless=true"])

def run_dash():
    """Run Dash dashboard"""
    print("🚀 Starting Dash...")
    subprocess.run([sys.executable, "dashboard.py"])

def open_browsers():
    """Open both dashboards in browser"""
    time.sleep(5)  # Wait longer for servers to start
    webbrowser.open("http://localhost:8501")  # Streamlit
    time.sleep(2)
    webbrowser.open("http://localhost:8050")  # Dash

def main():
    print("🚀 Launching Financial Dashboards...")

    try:
        system_initializer.initialize_system()
        print("\nAvailable dashboards:")

        print(
            "📊 Streamlit: "
            "http://localhost:8501"
        )

        print(
            "📈 Dash: "
            "http://localhost:8050"
        )
        
        print(
            "✓ System initialization completed."
        )
        
        # Start both servers with delay
        t1 = threading.Thread(
            target=run_dash,
            name="DashThread"
        ) # Dash first (takes longer to fail)

        t2 = threading.Thread(
            target=run_streamlit,
            name="StreamlitThread"
        ) # Then Streamlit
        
        t1.start()
        time.sleep(3)  # Give Dash time to start
        t2.start()
        
        # Open browsers after both start
        open_browsers()
        
        print("✅ Both dashboards should be running!")
        print("Press Ctrl+C to stop all servers")
        
        
        t1.join()
        t2.join()

    except KeyboardInterrupt:

        print("\n🛑 Shutting down servers...")

    except Exception as exc:

        print(
            f"\n❌ Launcher failed:\n{exc}"
        )

if __name__ == "__main__":
    main()
    