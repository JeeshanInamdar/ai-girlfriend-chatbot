# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency definitions and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all local project files into the container
COPY . .

# Run the Flask app using Gunicorn on the port Cloud Run specifies
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]