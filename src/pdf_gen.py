import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from email_sender import send_email
import os

def file_exists(path):
    return os.path.isfile(path)

def generator(primary_category=None, secondary_category=None, brand=None):
    print(f"Generating PDF catalogue for: {primary_category}, {secondary_category}, {brand}")

    # Load data from a local CSV file
    df = pd.read_excel("utils/data.xlsx")
    print(f"Debug - Available columns: {df.columns.tolist()}")

    # Filter rows based on the inputs
    filtered_df = df.copy()
    if primary_category:
        filtered_df = filtered_df[filtered_df["Primary Category"].str.lower() == primary_category.lower()]
    if secondary_category:
        filtered_df = filtered_df[filtered_df["Secondary Category"].str.lower() == secondary_category.lower()]
    if brand:
        filtered_df = filtered_df[filtered_df["Brand"].str.lower() == brand.lower()]

    print(f"Debug - Found {len(filtered_df)} matching rows")

    # Add serial number column
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df['sno'] = filtered_df.index + 1

    # Determine the template to use based on the primary category
    if primary_category:
        template_name = f"src/layouts/{primary_category.lower().replace(' ', '')}.html"
        if not file_exists(template_name):
            print(f"Debug - Template {template_name} not found. Reverting to default template.")
            template_name = "src/layouts/powertools.html"
    else:
        template_name = "src/layouts/powertools.html"

    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader("."))
    env.filters['file_exists'] = file_exists  # Register the custom filter
    template = env.get_template(template_name)

    # Convert "Price" column to int
    if "Price" in filtered_df.columns:
        filtered_df["Price"] = filtered_df["Price"].astype(int)
    
    # Render template with filtered DataFrame data
    html_content = template.render(data=filtered_df.to_dict(orient="records"), sub_head=f"{primary_category or ''} {secondary_category or ''}  {brand or ''}")

    # Define the output PDF path
    primary_filename = primary_category.lower().strip().replace(" ", "-") if primary_category else "catalogue"
    filename = primary_filename
    if secondary_category:
        secondary_filename = secondary_category.lower().strip().replace(" ", "-")
        filename = f"{primary_filename}_{secondary_filename}"
    if brand:
        brand_filename = brand.lower().strip().replace(" ", "-")
        filename = f"{filename}_{brand_filename}"
    output_pdf_path = f"{filename}.pdf"

    # Convert to PDF
    HTML(string=html_content, base_url='.').write_pdf(output_pdf_path)
    print("PDF generated successfully!")

    # Send email
    send_email(subject=f"Catalogue for {primary_category or 'All'} - {secondary_category or 'All'} - {brand or 'All'}", attachment_path=output_pdf_path)
    print("Email sent successfully!")

def generate_tag_catalog(selected_tags):
    """
    Generate a catalog PDF based on selected tags.
    Items are grouped by primary category and rendered with the appropriate template.
    """
    print(f"Generating tagged catalog for tags: {selected_tags}")
    
    # Validate input
    if not selected_tags:
        print("No tags selected. Please select at least one tag.")
        return
    
    # Load and prepare data
    df = pd.read_excel("utils/data.xlsx")
    if "Price" in df.columns:
        df["Price"] = df["Price"].astype(int)
    
    # Filter by tags
    filtered_df = filter_by_tags(df, selected_tags)
    if len(filtered_df) == 0:
        print("No items found matching the selected tags.")
        return
    
    # Group by primary category
    category_groups = group_by_primary_category(filtered_df)
    print(f"Items spread across {len(category_groups)} primary categories")
    
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader("."))
    env.filters['file_exists'] = file_exists
    
    # Render each group with appropriate template
    html_sections = []
    for category, group_df in category_groups.items():
        html = render_category_section(env, category, group_df)
        if html:
            html_sections.append({
                'category': category,
                'content': html
            })
    
    # Generate combined HTML
    full_html = combine_html_sections(env, html_sections, selected_tags)
    
    # Generate PDF
    output_filename = generate_pdf_filename(selected_tags)
    output_path = f"{output_filename}.pdf"
    HTML(string=full_html, base_url='.').write_pdf(output_path)
    print(f"PDF generated successfully! ({len(filtered_df)} items)")
    
    # Send email
    email_subject = f"Tagged Catalog: {', '.join(selected_tags[:3])}"
    if len(selected_tags) > 3:
        email_subject += f" and {len(selected_tags)-3} more"
    
    send_email(subject=email_subject, attachment_path=output_path)
    print("Email sent successfully!")
    
    return output_path

def filter_by_tags(df, tags):
    """Filter DataFrame to only include rows with matching tags."""
    def has_matching_tag(tag_string):
        if not isinstance(tag_string, str):
            return False
        item_tags = [t.strip() for t in tag_string.split(',')]
        return any(tag in tags for tag in item_tags) # returns bool(x) for any x in iteratable 
    
    filtered_df = df[df['Tags'].apply(has_matching_tag)]
    
    # Log summary of filtered data
    print(f"Found {len(filtered_df)} matching rows")
    if not filtered_df.empty:
        category_counts = filtered_df.groupby('Primary Category').size()
        for category, count in category_counts.items():
            print(f"- {category}: {count} items")
    
    return filtered_df

def group_by_primary_category(df):
    """Group DataFrame rows by primary category and add serial numbers."""
    groups = {}
    print(f"Data received to group_by_pc:\n{df}")
    for category, group in df.groupby('Primary Category'):
        # Add serial numbers within each group
        group_df = group.copy()
        group_df.reset_index(drop=True, inplace=True)
        group_df['sno'] = group_df.index + 1
        groups[category] = group_df
        
    
    print(f"Data after processing:\n{groups}")
    return groups

def get_template_for_category(category):
    """Get the appropriate template name for a given primary category."""
    template_name = f"src/layouts/{category.lower().replace(' ', '')}.html"
    if not file_exists(template_name):
        print(f"Template not found for {category}, using default template.")
        template_name = "src/layouts/powertools.html"
    return template_name

def render_category_section(env, category, df):
    """Render HTML for a specific category using its template."""
    template_name = get_template_for_category(category)
    template = env.get_template(template_name)
    
    try:
        html = template.render(
            data=df.to_dict(orient="records"),
            sub_head=f"{category} - Selected Items",
            exclude_terms = True
        )
        return html
    except Exception as e:
        print(f"Error rendering template for {category}: {e}")
        return None

def combine_html_sections(env, sections, tags):
    """Combine multiple HTML sections into a single document."""
    if len(sections) == 1:
        # Only one category, use its HTML directly
        return sections[0]['content']
    
    # Multiple categories need a wrapper
    wrapper_template = create_wrapper_template(env)
    
    # Create title based on tags
    if len(tags) <= 3:
        title = f"Items Tagged: {', '.join(tags)}"
    else:
        title = f"Items Tagged: {', '.join(tags[:3])} and {len(tags)-3} more"
    
    # Render the wrapper with all sections
    return wrapper_template.render(
        sections=sections,
        title=title
    )

def create_wrapper_template(env):
    """
    Get the wrapper template for combining multiple HTML sections.
    """
    wrapper_path = "src/layouts/wrapper.html"
    
    return env.get_template(wrapper_path)

def generate_pdf_filename(tags):
    """Generate a meaningful filename based on selected tags."""
    # Use first 3 tags in filename
    tag_part = "-".join([tag.lower().replace(" ", "_") for tag in tags[:3]])
    
    # Add count if more than 3 tags
    if len(tags) > 3:
        tag_part += f"_and_{len(tags)-3}_more"
    
    return f"tagged_{tag_part}"

if __name__ == '__main__':
    generator("Spare Parts", "ASM04-100A")