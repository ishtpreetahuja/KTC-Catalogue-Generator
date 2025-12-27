import os
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from email_sender import send_email

def file_exists(path):
    return os.path.isfile(path)


def to_uri(path):
    # Resolve to an absolute file:// URI so WeasyPrint can load local assets reliably
    return Path(path).resolve().as_uri()

def generator(primary_group=None, secondary_group=None, category=None):
    print(f"Generating PDF catalogue for: {primary_group}, {secondary_group}, {category}")

    # Load data from a local CSV file
    df = pd.read_csv("utils/data.csv")
    print(f"Debug - Available columns: {df.columns.tolist()}")

    # Filter rows based on the inputs
    filtered_df = df.copy()
    if primary_group:
        filtered_df = filtered_df[filtered_df["Primary Group"].str.lower() == primary_group.lower()]
    if secondary_group:
        filtered_df = filtered_df[filtered_df["Secondary Group"].str.lower() == secondary_group.lower()]
    if category:
        filtered_df = filtered_df[filtered_df["Category"].str.lower() == category.lower()]

    print(f"Debug - Found {len(filtered_df)} matching rows")

    # Add serial number column
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df['sno'] = filtered_df.index + 1

    # Determine the template to use based on the primary group
    if primary_group:
        template_name = f"src/layouts/{primary_group.lower().replace(' ', '')}.html"
        if not file_exists(template_name):
            print(f"Debug - Template {template_name} not found. Reverting to default template.")
            template_name = "src/layouts/powertools.html"
    else:
        template_name = "src/layouts/powertools.html"

    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader("."))
    env.filters['file_exists'] = file_exists  # Register the custom filter
    env.filters['to_uri'] = to_uri  # Ensure local assets resolve to file:// URIs
    template = env.get_template(template_name)

    # Convert "Price" column to int
    if "Price" in filtered_df.columns:
        filtered_df["Price"] = filtered_df["Price"].astype(int)
    
    # Render template with filtered DataFrame data
    html_content = template.render(data=filtered_df.to_dict(orient="records"), sub_head=f"{primary_group or ''} {secondary_group or ''}  {category or ''}")

    # Define the output PDF path
    primary_filename = primary_group.lower().strip().replace(" ", "-") if primary_group else "catalogue"
    filename = primary_filename
    if secondary_group:
        secondary_filename = secondary_group.lower().strip().replace(" ", "-")
        filename = f"{primary_filename}_{secondary_filename}"
    if category:
        category_filename = category.lower().strip().replace(" ", "-")
        filename = f"{filename}_{category_filename}"
    output_pdf_path = f"{filename}.pdf"

    # Convert to PDF
    HTML(string=html_content, base_url='.').write_pdf(output_pdf_path)
    print("PDF generated successfully!")

    # Send email
    send_email(subject=f"Catalogue for {primary_group or 'All'} - {secondary_group or 'All'} - {category or 'All'}", attachment_path=output_pdf_path)
    print("Email sent successfully!")

if __name__ == '__main__':
    generator("Spare Parts", "ASM04-100A")