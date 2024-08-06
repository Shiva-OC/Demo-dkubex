FROM python:3.10.10-slim-bullseye

# Set working directory
WORKDIR /app

# Install necessary dependencies and clean up to reduce image size
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository into a separate directory
RUN git clone https://github.com/Shiva-OC/Demo-dkubex.git repo

# Change working directory to the cloned repository
WORKDIR /app/repo

# Install Python dependencies from requirements.txt and the wheel file, ray
RUN pip3 install -r requirements.txt \
    && python -m pip install d3x_cli-x-py3-none-any.whl \
    && pip3 install ray

# Make the startup script executable
RUN chmod +x app_startup.sh

# Expose the port that Streamlit will run on
EXPOSE 8501

# Add a health check to ensure the container is running properly
HEALTHCHECK CMD curl --fail http://localhost:8501/healthz || exit 1

# Define the entry point for the container
ENTRYPOINT ["/app/repo/app_startup.sh"]
