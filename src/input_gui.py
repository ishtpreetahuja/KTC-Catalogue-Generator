import streamlit as st
import pandas as pd
from pdf_gen import generator
from sync_local import syncing
import time

# Set page title and favicon
st.set_page_config(
    page_title="Catalogue Generator",
    page_icon="📊"
)

# Load data from CSV
df = pd.read_csv("utils/data.csv")

# Get unique values for dropdowns
primary_group_options = df["Primary Group"].unique().tolist()
secondary_group_options = df["Secondary Group"].unique().tolist()
category_options = df["Category"].unique().tolist()

def clear_text(): # this is the function you define (def is a Python keyword and is short for 'define')
  st.session_state["primary_group"] = ''  # add "text" as a key using the square brackets notation and set it to have the value ''
  st.session_state["secondary_group"] = ''  # add "text" as a key using the square brackets notation and set it to have the value ''
  st.session_state["category"] = ''  # add "text" as a key using the square brackets notation and set it to have the value ''

def main():
    # Initialize session state for input values
    if 'reset_inputs' not in st.session_state:
        st.session_state.reset_inputs = False

    st.title("Catalogue Generator")

    # Dropdowns for user input
    if st.session_state.reset_inputs:
        primary_group = st.selectbox("Primary Group", [""] + primary_group_options, key="primary_group", index=0)
        secondary_group = st.selectbox("Secondary Group", [""] + secondary_group_options, key="secondary_group", index=0)
        category = st.selectbox("Category", [""] + category_options, key="category", index=0)
        st.session_state.reset_inputs = False
    else:
        primary_group = st.selectbox("Primary Group", [""] + primary_group_options, key="primary_group")
        secondary_group = st.selectbox("Secondary Group", [""] + secondary_group_options, key="secondary_group")
        category = st.selectbox("Category", [""] + category_options, key="category")

    # Buttons for generating PDF and syncing data
    if st.button("Generate PDF"):
        with st.spinner('Generating PDF...'):
            generator(primary_group, secondary_group, category)
            st.success("PDF generated successfully and email sent!")
            time.sleep(5)
            st.rerun()

    if st.button("Sync Data"):
        with st.spinner('Syncing data...'):
            syncing()
            st.success("Data synced successfully!")
            time.sleep(5)
            st.rerun()

    st.button("Create New Entry", on_click=clear_text)

if __name__ == "__main__":
    main()