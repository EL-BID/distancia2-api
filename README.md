

## Instalación de Dependencias

Las siguientes instrucciones son para realizar las dependencias de la aplicación en sistema operativo Ubuntu, tales con bases de datos.

### MySQL

How To Install MySQL on Ubuntu 18.04
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04

sudo apt update
sudo apt install mysql-server
sudo apt install libmysqlclient-dev
sudo mysql

sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address            = 0.0.0.0
sudo systemctl restart mysql

CREATE USER 'dist2_app'@'%' IDENTIFIED BY 'distancia2.password';
GRANT ALL PRIVILEGES ON *.* TO 'dist2_app'@'%' WITH GRANT OPTION;
CREATE DATABASE distancia2;

### Nginx

sudo apt install nginx

### Redis

sudo apt install redis
