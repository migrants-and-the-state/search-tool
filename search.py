import os
import json
import streamlit as st
from jsonschema import validate, ValidationError

# Load the JSON schema
def load_schema(schema_path):
    with open(schema_path, 'r') as file:
        return json.load(file)

# Define a function to load and index the files
def load_files_from_folder(folder_path, schema):
    files_data = []
    count = 0
    print(os.listdir(folder_path)[:50])
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and ".DS_Store" not in filename:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                try:
                    data = json.load(file)  # Load the JSON data
                    # Validate against schema
                    validate(instance=data, schema=schema)
                    files_data.append(data)
                except json.JSONDecodeError:
                    st.error(f"Error reading {filename} (not a valid JSON)")
                except ValidationError as ve:
                    st.error(f"File {filename} failed schema validation: {ve.message}")
            count += 1
        if count == 1000:
            break 
    return files_data

# Search function for exact match on any attribute
def search_files(files_data, filters):
    results = []
    for file_data in files_data:
        match = True
        for key, value in filters.items():
            if key in file_data:
                # Handle exact match for top-level keys
                if isinstance(file_data[key], list):
                    if value not in file_data[key]:
                        match = False
                        break
                elif file_data[key] != value:
                    match = False
                    break
            # Handle nested attribute searches
            elif key == "cert_naturalization_attributes":
                for nested_key, nested_value in filters[key].items():
                    if nested_key in file_data.get('cert_naturalization_attributes', {}):
                        if nested_value[0] not in file_data['cert_naturalization_attributes'][nested_key]:
                            match = False
                            break
            elif key == "g325a_attributes":
                for nested_key, nested_value in filters[key].items():
                    if nested_key in file_data.get('g325a_attributes', {}):
                        if nested_value[0] not in file_data['g325a_attributes'][nested_key]:
                            match = False
                            break
        if match:
            results.append(file_data)
    return results

# Paginate the results
def paginate_results(results, page, results_per_page=20):
    start_idx = (page - 1) * results_per_page
    end_idx = start_idx + results_per_page
    return results[start_idx:end_idx]

# Streamlit app
st.title("File Search Application with Pagination and Detail View")

# Load the schema
schema_path = "/Users/ajay/Documents/Oncampus/extracted-data/docs/schema.json"  # Path to your schema.json
schema = load_schema(schema_path)

# Load the files from the folder
folder_path = "/Users/ajay/Documents/Oncampus/extracted-data/data/metadata_outputs"  # Change this to your folder path
files_data = load_files_from_folder(folder_path, schema)
st.write(f"Loaded {len(files_data)} files.")

# Create filters
st.sidebar.header("Search Filters")
is_g325a = st.sidebar.checkbox("is_g325a")
is_cert_naturalization = st.sidebar.checkbox("is_cert_naturalization")
afile_number = st.sidebar.text_input("Afile Number")
llm_name_at_naturalization = st.sidebar.text_input("Name at Naturalization")
llm_naturalization_country = st.sidebar.text_input("Naturalization Country")

# Build the filters
filters = {}
if is_g325a:
    filters["is_g325a"] = True
if is_cert_naturalization:
    filters["is_cert_naturalization"] = True
if afile_number:
    filters["afile_number"] = afile_number
if llm_name_at_naturalization:
    filters["cert_naturalization_attributes"] = {"LLM_NAME_AT_NATURALIZATION": [llm_name_at_naturalization]}
if llm_naturalization_country:
    filters["cert_naturalization_attributes"] = {"LLM_NATURALIZATION_COUNTRY": [llm_naturalization_country]}

# Run search
if st.sidebar.button("Search"):
    results = search_files(files_data, filters)
    
    if results:
        st.write(f"Found {len(results)} results")

        # Pagination
        total_pages = (len(results) - 1) // 20 + 1
        selected_page = st.selectbox("Select page", list(range(1, total_pages + 1)))

        paginated_results = paginate_results(results, selected_page)

        # Display results in tiles with buttons to view details
        for i, result in enumerate(paginated_results):
            afile_number = result.get('afile_number')
            doc_id = result.get('doc_id')  # Assuming doc_id is unique
            unique_key = f"{afile_number}_{doc_id}_{i}"  # Create a unique key
            if st.button(f"View details for Afile Number {afile_number}", key=unique_key):
                st.session_state['selected_result'] = result  # Save result in session state
                break

    else:
        st.write("No results found.")

# Display selected result details
if 'selected_result' in st.session_state:
    selected_result = st.session_state['selected_result']
    
    # Show selected result in two columns (Image and JSON details)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(selected_result.get('url'), width=400)

    with col2:
        st.write("**File Details:**")
        st.json(selected_result)