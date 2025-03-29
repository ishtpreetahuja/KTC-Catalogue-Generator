import streamlit as st
import pandas as pd
from pdf_gen import generator, generate_tag_catalog
from sync_local import syncing
import time
import os

# Set page title and favicon
st.set_page_config(
    page_title="Catalogue Generator",
    page_icon="📊"
)

# Load data from Excel
df = pd.read_excel("utils/data.xlsx")

# Get unique values for dropdowns
primary_categories = df["Primary Category"].unique().tolist()
secondary_categories = df["Secondary Category"].unique().tolist()
brands = df["Brand"].unique().tolist()

# Load unique tags from file
def load_tags():
    tags = []
    if os.path.exists("utils/unique_tags.txt"):
        with open("utils/unique_tags.txt", "r") as f:
            tags = [line.strip() for line in f.readlines()]
    return tags

def clear_category_filters():
    st.session_state["primary_category"] = ''
    st.session_state["secondary_category"] = ''
    st.session_state["brand"] = ''

def clear_tag_filters():
    st.session_state["selected_tags"] = []

def main():
    # Initialize session state
    if 'reset_inputs' not in st.session_state:
        st.session_state.reset_inputs = False
    
    if 'filter_mode' not in st.session_state:
        st.session_state.filter_mode = "category"
    
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []

    # Load tags inside the function to ensure proper scope
    tags = load_tags()

    st.title("Catalogue Generator")
    
    # Filter mode toggle
    filter_mode = st.radio(
        "Select Filtering Mode",
        ["Category Filter", "Tag Filter"],
        index=0 if st.session_state.filter_mode == "category" else 1,
        key="filter_mode_radio"
    )
    
    # Update session state based on selection
    st.session_state.filter_mode = "category" if filter_mode == "Category Filter" else "tag"
    
    # Create two columns for better layout
    col1, col2 = st.columns([3, 1])
    
    # Variables to hold filter values
    primary_category = None
    secondary_category = None
    brand = None
    selected_tags = []
    
    with col1:
        # Category-based filtering
        if st.session_state.filter_mode == "category":
            st.subheader("Category Filters")
            
            # Show category dropdowns
            primary_category = st.selectbox(
                "Primary Category", 
                [""] + primary_categories, 
                key="primary_category"
            )
            
            secondary_category = st.selectbox(
                "Secondary Category", 
                [""] + secondary_categories, 
                key="secondary_category"
            )
            
            brand = st.selectbox(
                "Brand", 
                [""] + brands, 
                key="brand"
            )
            
            # Clear filters button
            st.button("Clear Category Filters", on_click=clear_category_filters)
            
        # Tag-based filtering
        else:
            st.subheader("Tag Filters")
            
            if not tags:
                st.warning("No tags found. Please sync data first.")
            else:
                # Multi-select for tags
                selected_tags = st.multiselect(
                    "Select Tags (items matching ANY selected tag will be included)",
                    options=tags,
                    default=st.session_state.selected_tags,
                    key="selected_tags"
                )
                
                # Show number of selected tags
                if selected_tags:
                    st.info(f"Selected {len(selected_tags)} tags")
                
                # Clear filters button
                st.button("Clear Tag Filters", on_click=clear_tag_filters)
    
    with col2:
        st.subheader("Actions")
        
        # Generate PDF button
        if st.button("Generate PDF", key="generate_btn"):
            with st.spinner('Generating PDF...'):
                if st.session_state.filter_mode == "category":
                    # Use category-based filtering
                    generator(primary_category, secondary_category, brand)
                else:
                    # Use dedicated tag-based filtering function
                    generate_tag_catalog(selected_tags)
                
                st.success("PDF generated successfully!")
                time.sleep(3)
        
        # Sync data button
        if st.button("Sync Data", key="sync_btn"):
            with st.spinner('Syncing data...'):
                syncing()
                # Reload tags after syncing
                st.session_state.selected_tags = []
                st.success("Data synced successfully!")
                time.sleep(2)
                st.rerun()

if __name__ == "__main__":
    main()