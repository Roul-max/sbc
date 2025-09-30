# Use specific Python version
FROM python:3.12.14-slim

# Set working directory inside container
WORKDIR /app

# Copy backend code into container
COPY . /app

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your app will run on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
