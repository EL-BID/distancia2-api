# Soporte de GPU

El algoritmo de procesamiento de imagenes del sistema Distancia2 posee la capacidad de
implementar la inferencia utilizando tarjetas gráfica disponibles en el servidor con el objetivo
optimizar la velocidad de ejecución del software. 

Para la ejecucion del sistema basado en GPU se utiliza la libreria tensorflow, la cual
tiene mayor soporte en tarjetas graficas de la marca Nvidia. Para una ejecución optima se recomienda
utilizar uno de los siguientes modelos con un *Compute Capability* mayor o igual a **6.1** disponibles
en el mercado link de soporte de tarjetas [Soporte CUDA](https://developer.nvidia.com/cuda-gpus).

Será necesaria la instalación de los drivers de la tarjeta grafica, las librerias de cuda y tensorflow.

Verificar tarjetas graficas instaladas
```
lspci | grep VGA
```

Agregar repositorios de paquetes de Nvidia
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
trobleshoot wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | sudo apt-key add -
sudo dpkg -i cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
sudo apt-get update
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt-get update
```

Instalar drivers de Nvidia
```
sudo apt-get install --no-install-recommends nvidia-driver-450
sudo reboot
```

verificar driver instalado
```
nvidia-smi
```

Instalar librerias de desarrollo y producción (~4GB)
```
sudo apt-get install --no-install-recommends \
    cuda-10-1 \
    libcudnn7=7.6.5.32-1+cuda10.1  \
    libcudnn7-dev=7.6.5.32-1+cuda10.1
```

Instalacion de TensorRT. Se requiere haber instalado libcudnn7 del comando anterior
```
sudo apt-get install -y --no-install-recommends libnvinfer6=6.0.1-1+cuda10.1 \
    libnvinfer-dev=6.0.1-1+cuda10.1 \
    libnvinfer-plugin6=6.0.1-1+cuda10.1
```

Agregar variables de entorno de CUDA al final del archivo
```
sudo nano .bashrc
# Included to Distancia2 project
PATH=$PATH:/usr/local/cuda-10.1/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.1/lib64
```

Guardar el archivo y reiniciar el servidor
```
sudo reboot
```

Se instala la versión de tensorflow correspondiente a la GPU
```
conda activate /opt/dist2/env
pip install tensorflow-gpu==2.2.0
```

Para mas información links de interes sobre la libreria consultar:

- https://www.tensorflow.org/install/gpu#ubuntu_1804_cuda_101
