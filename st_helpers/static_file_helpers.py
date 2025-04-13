import os
import shutil
from pathlib import Path
import streamlit as st

def move_font_files():
    STREAMLIT_STATIC_PATH = Path(st.__path__[0]) / "static"
    CSS_PATH = STREAMLIT_STATIC_PATH / "fonts/"
    if not CSS_PATH.is_dir():
        CSS_PATH.mkdir()

    font_file = CSS_PATH / "balsamiq-sans-700.woff2"
    if not font_file.exists():
        shutil.copy("fonts/balsamiq-sans-700.woff2", font_file)
    font_file = CSS_PATH / "balsamiq-sans-700italic.woff2"
    if not font_file.exists():
        shutil.copy("fonts/balsamiq-sans-700italic.woff2", font_file)
    font_file = CSS_PATH / "balsamiq-sans-italic.woff2"
    if not font_file.exists():
        shutil.copy("fonts/balsamiq-sans-italic.woff2", font_file)
    font_file = CSS_PATH / "balsamiq-sans-regular.woff2"
    if not font_file.exists():
        shutil.copy("fonts/balsamiq-sans-regular.woff2", font_file)
    font_file = CSS_PATH / "delius-regular.woff2"
    if not font_file.exists():
        shutil.copy("fonts/delius-regular.woff2", font_file)
    css_file = CSS_PATH / "styles.css"
    if not css_file.exists():
        shutil.copy("styles.css", css_file)
