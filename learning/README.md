Explanation to get started: TODO

Run the following in WSL to start the Jupyter server:

    docker run -u $(id -u):$(id -g) --gpus all \
        -it --rm -p 8888:8888 \
        -v /mnt/c/dev/ai-and-lego:/project -w /project \
        -v $PWD/jupyter-config:/.jupyter \
        tensorflow/tensorflow:latest-gpu-jupyter \
        jupyter-lab --ip=0.0.0.0