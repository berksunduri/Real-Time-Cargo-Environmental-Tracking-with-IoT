FROM python:3.9-slim-buster

WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt requirements.txt

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code from your host to your image filesystem.
COPY . .

EXPOSE 5000

CMD ["python", "main.py"]