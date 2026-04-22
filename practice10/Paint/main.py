from pathlib import Path
import runpy


# Redirect paint entrypoint to racer so this project runs Racer only.
if __name__ == "__main__":
    racer_main = Path(__file__).resolve().parents[1] / "racer" / "main.py"
    runpy.run_path(str(racer_main), run_name="__main__")
