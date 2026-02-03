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


## Acknowledgments / Reconocimientos

**Copyright © [2025]. Inter-American Development Bank ("IDB"). Authorized Use.**  
The procedures and results obtained based on the execution of this software are those programmed by the developers and do not necessarily reflect the views of the IDB, its Board of Executive Directors or the countries it represents.

**Copyright © [2025]. Banco Interamericano de Desarrollo ("BID"). Uso Autorizado.**  
Los procedimientos y resultados obtenidos con la ejecución de este software son los programados por los desarrolladores y no reflejan necesariamente las opiniones del BID, su Directorio Ejecutivo ni los países que representa.

### Support and Usage Documentation / Documentación de Soporte y Uso

**Copyright © [2025]. Inter-American Development Bank ("IDB").** The Support and Usage Documentation is licensed under the Creative Commons License CC-BY 4.0 license. The opinions expressed in the Support and Usage Documentation are those of its authors and do not necessarily reflect the opinions of the IDB, its Board of Executive Directors, or the countries it represents.

**Copyright © [2025]. Banco Interamericano de Desarrollo (BID).** La Documentación de Soporte y Uso está licenciada bajo la licencia Creative Commons CC-BY 4.0. Las opiniones expresadas en la Documentación de Soporte y Uso son las de sus autores y no reflejan necesariamente las opiniones del BID, su Directorio Ejecutivo ni los países que representa.

### AI-Powered Services Disclaimer / Exención de responsabilidad por Servicios Impulsados por IA

The Software may include features which use, are powered by, or are an artificial intelligence system (“AI-Powered Services”), and as a result, the services provided via the Software may not be completely error-free or up to date. Additionally, the User acknowledges that due to the incorporation of AI-Powered Services in the Software, the Software may not dynamically (in “real time”) retrieve information and that, consequently, the output provided to the User may not account for events, updates, or other facts that have occurred or become available after the Software was trained. Accordingly, the User acknowledges that the use of the Software, and that any actions taken or reliance on such products, are at the User’s own risk, and the User acknowledges that the User must independently verify any information provided by the Software.

El Software puede incluir funciones que utilizan, están impulsadas por o son un sistema de inteligencia artificial (“Servicios Impulsados por IA”) y, como resultado, los servicios proporcionados a través del Software pueden no estar completamente libres de errores ni actualizados. Además, el Usuario reconoce que, debido a la incorporación de Servicios Impulsados por IA en el Software, este puede no recuperar información dinámicamente (en “tiempo real”) y que, en consecuencia, la información proporcionada al Usuario puede no reflejar eventos, actualizaciones u otros hechos que hayan ocurrido o estén disponibles después del entrenamiento del Software. En consecuencia, el Usuario reconoce que el uso del Software, y que cualquier acción realizada o la confianza depositada en dichos productos, se realiza bajo su propio riesgo, y reconoce que debe verificar de forma independiente cualquier información proporcionada por el Software.
