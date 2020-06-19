













### MySQL

How To Install MySQL on Ubuntu 18.04
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04


sudo apt update
sudo apt install mysql-server libmysqlclient-dev
sudo mysql

```
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```
> bind-address = 0.0.0.0

sudo systemctl restart mysql

```
CREATE USER 'dist2_app'@'%' IDENTIFIED BY 'distancia2.password';
GRANT ALL PRIVILEGES ON *.* TO 'dist2_app'@'%' WITH GRANT OPTION;
CREATE DATABASE distancia2;
```

### Nginx

sudo apt install nginx

### Redis

sudo apt install redis

## Instalación y configuracion de backend

### Previo

sudo apt intall git build-essential

sudo apt update
sudo apt install build-essential 

### Instalacion de python

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh
y seguir instrucciones... (acepto, si, si etc TODO EN SI)

### Instalacion de backend



se crea la carpeta del proyecto y se cambian los permisos
sudo mkdir /opt/dist2; sudo chmod 777 /opt/dist2
cd /opt/dist2
git clone https://gitlab.com/josch_san/distancia2-api.git
santanaelectronica@gmail.com

## crea entorno virtual para instalacion en produccion
conda create -y -p /opt/dist2/env python=3.7
conda activate /opt/dist2/env

## instala paquetes de python en el entorno virtual
/opt/dist2/env/bin/pip install -r distancia2-api/requirements.txt

## en caso de poseer una tarjeta grafica
pip install tensorflow-gpu==2.2.0

cd distancia2-api

## este es un archivo con variables de configuracion que podemos editar como conexion a BD entre otras cosas
cp distancia2/devel.env distancia2/prod.env

## crea los esquemas de la BD mysql
python manage.py makemigrations cams
python manage.py migrate

## con esto probamos que se instalo sin problemas y probar en el navegador http://localhost:8000/api
python manage.py runserver

## debe dar esta informacion
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 04, 2020 - 01:24:00
Django version 3.0.6, using settings 'distancia2.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.


## crea el usuario con acceso al panel de admin
python manage.py createsuperuser

## recolecta (no se que palabra) los archivos estaticos (html, css, js) que necesita el backend para el panel de admin
python manage.py collectstatic

## copia el archivo de configuracion para el servidor web de produccion (nginx) y reinicia
sudo rm /etc/nginx/sites-enabled/default
sudo cp /opt/dist2/distancia2-api/production/distancia2.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/distancia2.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx

## Se copia el archivo de configuracion del servicio de produccion para el backend, y se habilita
sudo cp /opt/dist2/distancia2-api/production/gunicorn.service /etc/systemd/system
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

## Hasta aqui esta instalado el backend en produccion
## Se pueden agregar configuraciones de camaras desde http://localhost/admin
## en primera instancia lo haremos nosotros


copiar codigo de yolo-coco
asi se llama la red de reconocimiento, pero se lo copiaron de algun lado y despues lo adaptaron

## Instalacion de frontend

estos paquetes su utilizan para compilar el codigo fuente del frontend
sudo apt install nodejs -y

cd /opt/dist2
git clone https://gitlab.com/josch_san/distancia2-web.git
cd distancia2-web/

## instala dependencias del frontend
npm install

## se configura lo que se necesite, porque va a depender del servidor en el que se instale, la direccion ip o el dns
cp .env.development .env.production

## editar direccion ip del servidor en la red correspondiente
nano .env.production

## compila el codigo fuente para produccion
npm run-script build
