# Use official Python image as base
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 9091

# Set default command (adjust as needed)
CMD ["python", "src/main.py"]
