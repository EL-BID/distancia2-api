# Manual de despliegue del sistema Distancia2

## Recursos de hardware

Requisitos mínimos del servidor:
- Procesador de al menos 8 cores i7
- 16 GB RAM
- GPU con capacidad de cómputo superior a 6.0
- 100 GB de espacio en disco

## Recursos de software

Sistema operativo Ubuntu 18.04 o superior

## Instalación y configuración de servicios y dependencias

### MySQL

```
sudo apt update
sudo apt install mysql-server libmysqlclient-dev
```

Editar la dirección IP en el archivo de configuración de MySQL para poder ser accedido desde un
cliente externo al servidor
```
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
```

Reiniciar el servicio para aplicar los cambios
```
sudo systemctl restart mysql
```

Crear el usuario y la tabla que usará la aplicación para acceder a la base de datos
```
sudo mysql
CREATE USER 'dist2_app'@'%' IDENTIFIED BY 'distancia2.password';
GRANT ALL PRIVILEGES ON *.* TO 'dist2_app'@'%' WITH GRANT OPTION;
CREATE DATABASE distancia2;
exit;
```
### Nginx y Redis
```
sudo apt install nginx redis
```

## Backend

### Dependencias
```
sudo apt update
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt install git git-lfs curl build-essential libsm6 libxext6 libxrender-dev
git lfs install
```

### Python
```
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh
```

En el formulario de instalación se presentará los términos licencia del software que deberan ser aceptados,
se puede mantener el directorio por defecto de instalación y hay que habilitar la inicialización de miniconda
que por defecto va deshabilitado.

### Configuración
Creación de carpeta para el proyecto, asignación de permisos y bajada del repositorio
```
sudo mkdir /opt/dist2; sudo chmod 777 /opt/dist2
mkdir /opt/dist2/logs
cd /opt/dist2
git clone https://github.com/EL-BID/distancia2-api.git
```

Armado del entorno virtual para instalación y despliegue
```
conda create -y -p /opt/dist2/env python=3.7
conda activate /opt/dist2/env
```

Instalación paquetes de Python en el entorno virtual
```
/opt/dist2/env/bin/pip install -r distancia2-api/requirements.txt
```

Configuración de GPU:
En caso de contar con una tarjeta gráfica, puede acceder al instructivo para realizar
la instalación basada en GPU: [Instalación de GPU](https://github.com/EL-BID/distancia2-api/blob/master/GPU_INSTALL.md)

Creación de los esquemas en la Base de Datos
```
cd /opt/dist2/distancia2-api
cp distancia2/devel.env distancia2/prod.env
python manage.py makemigrations cams
python manage.py migrate
```

El archivo copiado contiene variables de configuración de la base de datos que puede
ser editado en caso de ser necesario. Los ajustes principales serian cambiar la configuración
a produccion `DEBUG=false` y la dirección IP del servidor `APP_HOST='<direccion_ip>'`.
```
nano distancia2/prod.env
python manage.py runserver
```

Nota: En caso de utilizar la configuración con GPU debe editar tambien los parametros
`MODEL_ENABLE_GPU=true`, comentar el parametro `# MODEL_WEIGHTS_PATH='yolo-coco/yolov3.weights'`
y descomentar `MODEL_WEIGHTS_PATH='yolo-coco/tf2/yolov3_weights.tf'`

Debe arrojar la siguiente información
```
Watching for file changes with StatReloader

Performing system checks...

System check identified no issues (0 silenced).
June 04, 2020 - 01:24:00
Django version 3.0.6, using settings &#39;distancia2.settings&#39;
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Creación de usuario con acceso al panel de administración y recopilación de archivos estáticos
(html, css, js) necesarios para el panel de administración
```
python manage.py createsuperuser
python manage.py collectstatic
```

Copia el archivo de configuracion para el servidor web de producción
```
sudo rm /etc/nginx/sites-enabled/default
sudo cp /opt/dist2/distancia2-api/production/distancia2.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/distancia2.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

Será necesario cambiar el parametro `server_name` en el archivo de configuración
con la direccion ip correspondiente
```
sudo nano /etc/nginx/sites-available/distancia2.conf
server_name <direccion_ip>;
```

Se habilita el archivo de configuración del servicio para el backend
```
sudo cp /opt/dist2/distancia2-api/production/gunicorn.service /etc/systemd/system
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

Para verificar que se instaló correctamente se puede probar el acceso a través del
navegador `http://<direccion_ip>/api`. Es posible editar las configuraciones de cámaras
desde `http://localhost/admin`

Es necesario copiar el modelo que se utilizará (en este caso yolo-coco)
y configurarlo en las variables del archivo `distancia2/prod.env`

## Frontend
Instalación de Node.js
```
cd ~
curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt install nodejs
```

Compilación del código fuente del frontend
```
cd /opt/dist2
git clone https://github.com/EL-BID/distancia2-web.git
```

Instalación de dependencias. Puede variar en función al servidor en el que se instale,
la dirección IP o el DNS.
```
cd /opt/dist2/distancia2-web/
npm install
cp .env.development .env.production
```

Editar la url en que se encuentra desplegado el backend del servidor en la red
correspondiente sin el puerto
```
nano .env.production
REACT_APP_API_URL=http://<direccion_ip>/api
```

y compilar del código fuente para producción. En caso de que presente un error de compilación
consultar la sección de Troubleshoots.
```
npm run-script build
```

Despues de desplegar el frontend ya podrá hacer las configuraciones de las cámaras a traves de la
interfazde administrador.

## Procesador de Cámaras

Para instalar y habilitar el servicio que se encarga de analizar las cámaras se ejecuta lo siguiente
```
sudo cp /opt/dist2/distancia2-api/production/camprocess.service /etc/systemd/system
sudo systemctl enable camprocess
sudo systemctl start camprocess
```

## Proceso de agrupación de datos

Con el objetivo de hacer mas ligera la lectura de los datos correspondientes a los registros capturados
por las cámaras asociadas al sistema, existe este proceso el cual agrupa los datos en ventanas de tiempo
de media hora lo cual facilita la lectura por parte de los tableros de control estadisticos de los datos.

Este proceso se anexa al cron del sistema operativo para ejecutarse cada media hora y se almacenan en una tabla
adicional de la base de datos. Para ello debe agregar la instrucción en la ultima linea de configuración del cron.
```
sudo EDITOR=nano crontab -e
5,35 * * * * cd /opt/dist2/distancia2-api && /opt/dist2/env/bin/python /opt/dist2/distancia2-api/group_records_routine.py
```

## Troubleshoots

### FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory

Durante el proceso de compilación del frontend es posible que muestre un mensaje de que se quede sin memoria.
Esto ocurre porque en algunas instalaciones queda  una catidad de memoria máxima especifica que se utilizará
durante el proceso de compilacion y tal vez necesite mas que esa cantidad, en ese caso pondemos ejecutar el comando
`npm run-script build` con un parametro para cambiar la cantidad de memoria que podrá utilizar.
```
NODE_OPTIONS="--max-old-space-size=4096" npm run-script build
```
