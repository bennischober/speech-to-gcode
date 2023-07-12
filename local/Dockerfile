FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Add current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable
ENV ENV=prod

# Make port 8050 available
EXPOSE 8050

# Run serve.py when the container launches
CMD ["python", "serve.py"]
