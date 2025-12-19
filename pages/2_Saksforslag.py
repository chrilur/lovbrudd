import streamlit as st
from pathlib import Path
from sidebar_utils import setup_page_header, add_sidebar_footer # Importer hjelperen

# Sett opp siden
st.set_page_config(page_title="Forslag til saker", layout="wide")

setup_page_header()

# Last inn og vis teksten
content = Path("markdown_filer/saksforslag.md").read_text(encoding="utf-8")
st.markdown(content)

add_sidebar_footer()