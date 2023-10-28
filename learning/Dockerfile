FROM tensorflow/tensorflow:latest-gpu-jupyter

# Install python packages from requirements.txt
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# Set working directory
WORKDIR /project

# Run jupyter-lab
CMD ["jupyter-lab", "--ip=0.0.0.0"]