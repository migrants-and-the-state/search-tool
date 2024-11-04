import os
import json
from whoosh.index import create_in
from whoosh.fields import *
import argparse


# Define the schema for the index
schema = Schema(
    document_type=TEXT(stored=True),
    is_cert_naturalization=BOOLEAN(stored=True),
    is_g325a=BOOLEAN(stored=True),
    countries=KEYWORD(stored=True, commas=True),
    years=KEYWORD(stored=True, commas=True),  # Changed to KEYWORD
    doc_id=ID(stored=True),
    afile_number=ID(stored=True),
    dev_idx=NUMERIC(stored=True),
    pagenumber=NUMERIC(stored=True),
    url=ID(stored=True),
    is_afile_redacted=BOOLEAN(stored=True),
    is_afile_withdrawn=BOOLEAN(stored=True),
    ocr_path=ID(stored=True),
    content=TEXT(stored=True)
)

# Create the index
if not os.path.exists("index"):
    os.mkdir("index")
ix = create_in("index", schema)

# Function to index a file
def index_file(writer, filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {filepath}")
            return
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {filepath}")
        return
    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")
        return
    
    # Add the document to the index
    writer.add_document(
        document_type=data.get('document_type', ''),
        is_cert_naturalization=data.get('is_cert_naturalization', False),
        is_g325a=data.get('is_g325a', False),
        countries=",".join(data.get('countries', [])),
        years=",".join(map(str, data.get('years', []))),  # Store years as comma-separated string
        doc_id=data.get('doc_id', ''),
        afile_number=data.get('afile_number', ''),
        dev_idx=data.get('dev_idx', 0),
        pagenumber=data.get('pagenumber', 0),
        url=data.get('url', ''),
        is_afile_redacted=data.get('is_afile_redacted', False),
        is_afile_withdrawn=data.get('is_afile_withdrawn', False),
        ocr_path=data.get('ocr_path', ''),
        content=json.dumps(data)  # Store the entire content as a JSON string
    )

# Index all files in the directory
def index_directory(directory):
    writer = ix.writer()
    for filename in os.listdir(directory):
        if filename != '.DS_Store' and os.path.isfile(os.path.join(directory, filename)):
            index_file(writer, os.path.join(directory, filename))
    writer.commit()

# Usage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index a directory of metadata outputs.")
    parser.add_argument("--path", type=str, required=True, help="Path to the directory to index.")
    
    args = parser.parse_args()
    index_directory(args.path)
    # index_directory()
    print("Indexing complete!")