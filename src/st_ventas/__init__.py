def main() -> None:
    """Indica como iniciar la aplicacion Streamlit."""
    import subprocess
    import sys

    from pathlib import Path

    app_path = Path(__file__).with_name("app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=False)
