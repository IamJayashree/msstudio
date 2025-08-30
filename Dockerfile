# Start from a standard Python 3.12 image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application files into the container
# This includes the server script and the entire 'mydir' folder
COPY qa_server.py .
COPY mydir/ ./mydir/
COPY index.html .

# Expose port 8082 to the outside world
EXPOSE 8082

# The command to run when the container starts
# This will launch your FastAPI server
CMD ["python", "qa_server.py"]