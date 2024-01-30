# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /Simulation

# Copy the current directory contents into the container at /Simulation
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir .

# Define environment variable
ENV NAME World

# Run Simulation when the container launches
CMD ["run_simulation"]