import streamlit as st
import json
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import query
import math

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = open_dir("index")

# Streamlit UI
st.title("Migrants and the State - Search by Document Content")

# Sidebar for filters
st.sidebar.title("Filters")

# Search boxes for each filter
document_type = st.sidebar.text_input("Document Type")
countries = st.sidebar.text_input("Countries")
doc_id = st.sidebar.text_input("Document ID")
afile_number = st.sidebar.text_input("A-File Number")

# Year range (optional)
start_year = st.sidebar.number_input("Start Year", min_value=1800, max_value=2100, value=None)
end_year = st.sidebar.number_input("End Year", min_value=1800, max_value=2100, value=None)

# Checkboxes
is_cert_naturalization = st.sidebar.checkbox("Is Certificate of Naturalization")
is_g325a = st.sidebar.checkbox("Is G-325A")
is_afile_redacted = st.sidebar.checkbox("Is A-File Redacted")
is_afile_withdrawn = st.sidebar.checkbox("Is A-File Withdrawn")

# Main search query
search_query = st.text_input("Enter search query")

# Function to perform search
def perform_search():
    with st.session_state.index.searcher() as searcher:
        # Build the query
        query_parts = []
        
        if search_query:
            query_parts.append(MultifieldParser(["document_type", "countries", "doc_id", "afile_number", "content"], st.session_state.index.schema).parse(search_query))
        
        # Add filters
        if document_type:
            query_parts.append(QueryParser("document_type", st.session_state.index.schema).parse(document_type))
        if countries:
            query_parts.append(QueryParser("countries", st.session_state.index.schema).parse(countries))
        if doc_id:
            query_parts.append(QueryParser("doc_id", st.session_state.index.schema).parse(doc_id))
        if afile_number:
            query_parts.append(QueryParser("afile_number", st.session_state.index.schema).parse(afile_number))
        
        # Year range (only if both start and end years are provided)
        if start_year is not None and end_year is not None:
            year_query = " OR ".join([str(year) for year in range(start_year, end_year + 1)])
            query_parts.append(QueryParser("years", st.session_state.index.schema).parse(year_query))
        
        # Checkboxes
        if is_cert_naturalization:
            query_parts.append(query.Term("is_cert_naturalization", True))
        if is_g325a:
            query_parts.append(query.Term("is_g325a", True))
        if is_afile_redacted:
            query_parts.append(query.Term("is_afile_redacted", True))
        if is_afile_withdrawn:
            query_parts.append(query.Term("is_afile_withdrawn", True))
        
        # Combine all query parts with AND
        final_query = query.And(query_parts) if query_parts else query.Every()
        
        results = searcher.search(final_query, limit=None)
        return [dict(r.items()) for r in results]  # Convert to list of dicts

# Search button
if st.button("Search"):
    st.session_state.results = perform_search()
    st.session_state.page = 1

# Pagination
ITEMS_PER_PAGE = 50

if 'results' in st.session_state:
    results = st.session_state.results
    total_pages = math.ceil(len(results) / ITEMS_PER_PAGE)
    
    st.write(f"Found {len(results)} results:")
    
    # Pagination controls
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col2:
        st.write(f"Page {st.session_state.page} of {total_pages}")
    with col3:
        if st.button("Next") and st.session_state.page < total_pages:
            st.session_state.page += 1
    
    # Display results for current page
    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_results = results[start_idx:end_idx]
    
    # Display results in a grid
    cols = st.columns(3)
    for i, result in enumerate(page_results):
        with cols[i % 3]:
            st.image(result['url'], caption=result['doc_id'], use_column_width=True)
            if st.button(f"View Details {start_idx + i}"):
                st.json(json.loads(result['content']))

st.sidebar.title("About")
st.sidebar.info("Migrants and the State")



