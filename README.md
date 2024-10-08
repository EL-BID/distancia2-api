# Distancia2 (Backend)

Distancia2 es un aplicación que permite analizar vídeo proveniente de cámaras,
detectando la cantidad de personas presentes en la imagen y calculando la distancia
entre cada persona con modelos de inteligencia artificial.

El proyecto está dividido en dos repositorios, uno correspondiente al backend que contiene el API
con la conexión a la base de datos, administración del contenido de la plataforma, procesos
automáticos entre otros scripts, mientras que el otro repositorio contiene el frontend solo con
con el código fuente para el despliegue de la interfaz web.

- [Repositorio Backend](https://github.com/EL-BID/distancia2-api)
- [Repositorio Frontend](https://github.com/EL-BID/distancia2-web)

## Características Principales

- Uso de librerías, dependendencias y tecnologias de software libre.
- Conexión sencilla y escalable para analisis de múltiples cámaras simultáneamente.
- Panel de visualización en tiempo real de las cámaras conectadas.
- Panel de adminstración de fácil uso para configuración de las cámaras.
- Almacenamiento de registros históricos en una base de datos, que permite un posterior analisis de los datos.
- En cada registro históricos se especifica información estadística y gráfica de la posición de cada personas.

## Tecnologías Utilizadas

- Python
- Tensorflow
- Django
- MySQL
- NGINX
- Redis
- React.js
- Plotly

## Modelo de Machine Learning utilizado

Como base para este proyecto se utiliza una versión personalizada a las necesidades del modelo yolo-coco perteneciente al proyecto open source **Darknet** que es un neural network framework escrito en C y CUDA. Para mas información diríjase al [vínculo del proyecto](https://github.com/pjreddie/darknet).

## Guia de Instalación

[Vínculo guia de instalación](https://github.com/EL-BID/distancia2-api/blob/master/DEPLOYMENT.md)

## Guia de Usuario

Ver anexo 2

## Licencia

[AM-331-A3 Licencia de Software](https://github.com/EL-BID/distancia2-api/blob/master/LICENSE.md)

## ¿Cómo contribuir?

Por favor comunicarse a través de la siguiente dirección de correo: ine-tsp@iadb.org

## Contribuidores

- [Joan Cerretani](https://www.linkedin.com/in/joancerretani/)
- [Joschuan Santana](https://www.linkedin.com/in/joschuansantana/)
- [José Maria Marquez](https://www.linkedin.com/in/jose-maria-marquez-blanco/)
- [Katherine Denis](https://www.linkedin.com/in/katherinedenis/)
