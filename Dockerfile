# Use the official Python image as a base
FROM python:3.8.18


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the Streamlit app with your specific parameters
CMD ["streamlit", "run", "search_and_ui.py", "--server.address=0.0.0.0"]