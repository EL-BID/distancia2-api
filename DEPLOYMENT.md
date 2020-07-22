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
### Nginx
```
sudo apt install nginx
```

### Redis
```
sudo apt install redis
```

## Backend

### Dependencias
```
sudo apt update
sudo apt install git build-essential libsm6 libxext6 libxrender-dev
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

En caso de contar con una tarjeta gráfica, ejecutar para rendimiento óptimo de la librería
```
pip install tensorflow-gpu==2.2.0
```

Creación de los esquemas en la Base de Datos
```
cd /opt/dist2/distancia2-api
cp distancia2/devel.env distancia2/prod.env
python manage.py makemigrations cams
python manage.py migrate
```

El archivo copiado contiene variables de configuración de la base de datos que puede
ser editado en caso de ser necesario. Los ajustes principales serian cambiar la configuración
a produccion `DEBUG=false` y la dirección IP del servidor `APP_HOST='<direccion_ip>'`
Para verificar que se instaló correctamente se puede probar el acceso a través del
navegador `http://<direccion_ip>/api`
```
nano distancia2/prod.env
python manage.py runserver
```

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

Se habilita el archivo de configuración del servicio para el backend
```
sudo cp /opt/dist2/distancia2-api/production/gunicorn.service /etc/systemd/system
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

Es posible editar las configuraciones de camaras desde `http://localhost/admin`

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

Editar la url en que se encuentra desplegado el backend del servidor en la red correspondiente
(ej. `http://<direccion_ip>/api`) y compilar del código fuente para producción
```
nano .env.production
npm run-script build
```

Despues de desplegar el frontend ya podrá hacer las configuraciones de las cámaras a traves de la
interfazde administrador.

## Procesador de Cámaras

Para instalar y habilitar el servicio que se encarga de analizar las cámaras se ejecuta lo siguiente
```
sudo cp /opt/dist2/distancia2-api/production/camprocess.service /etc/systemd/system
sudo systemctl start camprocess
sudo systemctl enable camprocess
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
