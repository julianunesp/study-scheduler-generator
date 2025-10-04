# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Update pip and install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/app/
COPY run.py /app/
COPY sample_spreadsheet.xlsx /app/

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run application when the container launches
CMD ["python", "run.py"]
