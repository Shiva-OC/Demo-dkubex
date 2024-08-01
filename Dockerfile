FROM python:3.10.10-slim-bullseye

WORKDIR /app

# Copy requirements file first for caching
COPY requirements.txt .

COPY d3x_cli-x-py3-none-any.whl .

RUN python -m pip install d3x_cli-x-py3-none-any.whl 

RUN pip3 install ray

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Clone the repository into a separate directory
RUN git clone https://github.com/Shiva-OC/Demo-dkubex.git repo

# Change working directory to the cloned repository
WORKDIR /app/repo

# Make the startup script executable
RUN chmod +x app_startup.sh

# Expose the port that Streamlit will run on
EXPOSE 8501

# Add a health check to ensure the container is running properly
HEALTHCHECK CMD curl --fail http://localhost:8501/healthz || exit 1

# Define the entry point for the container
ENTRYPOINT ["./app_startup.sh"]
