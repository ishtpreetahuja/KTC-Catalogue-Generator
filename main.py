import os

if __name__ == "__main__":
    os.environ["PYTHONPATH"] = os.path.abspath("src")
    os.system("python -m streamlit run src/input_gui.py")