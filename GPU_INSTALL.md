# Soporte de GPU

El algoritmo de procesamiento de imagenes del sistema Distancia2 posee la capacidad de
implementar la inferencia utilizando tarjetas gráfica disponibles en el servidor con el objetivo
optimizar la velocidad de ejecución del software. 

Para la ejecucion del sistema basado en GPU se utiliza la libreria tensorflow, la cual
tiene mayor soporte en tarjetas graficas de la marca Nvidia. Para una ejecución optima se recomienda
utilizar uno de los siguientes modelos con un *Compute Capability* mayor o igual a **6.1** disponibles
en el mercado link de soporte de tarjetas [Soporte CUDA](https://developer.nvidia.com/cuda-gpus).

Será necesaria la instalación de los drivers de la tarjeta graáfica, las librerias de cuda y tensorflow.

Nota: Es importante desabilitar el security boot a nivel del BIOS para que no interfiera con la
instalación de los drivers de la tarjeta gráfica.

Verificar tarjetas graficas instaladas
```
lspci | grep VGA
```

Agregar repositorios de paquetes de Nvidia
```
cd ~
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/ /"
sudo apt-get update
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt update
```

Instalar drivers de Nvidia y reiniciar
```
sudo apt -y install --no-install-recommends nvidia-driver-450
sudo reboot
```

verificar driver instalado
```
nvidia-smi
```

Instalar librerias de desarrollo y producción (~4GB)
```
wget https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/libnvinfer7_7.1.3-1+cuda11.0_amd64.deb
sudo apt install ./libnvinfer7_7.1.3-1+cuda11.0_amd64.deb
sudo apt update

sudo apt install --no-install-recommends \
    cuda-11-0 \
    libcudnn8=8.0.4.30-1+cuda11.0  \
    libcudnn8-dev=8.0.4.30-1+cuda11.0
```

Instalacion de TensorRT. Se requiere haber instalado libcudnn7 del comando anterior
```
sudo apt install -y --no-install-recommends libnvinfer7=7.1.3-1+cuda11.0 \
    libnvinfer-dev=7.1.3-1+cuda11.0 \
    libnvinfer-plugin7=7.1.3-1+cuda11.0
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

- https://www.tensorflow.org/install/gpu#ubuntu_1804_cuda_110


## Troubleshoots

### No se puede ejecutar el comando `sudo apt-key adv --fetch-keys`

En caso de que no se pueda agregar la llave, se puede utilizar este otro comando como remplazo.
```
wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | sudo apt-key add -
```