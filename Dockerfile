# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

COPY ai-based-hyper-local-marketing .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt



# Expose the port your app runs on
EXPOSE 5000

# Run the app
CMD ["python3", "run.py"]