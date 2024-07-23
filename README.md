# SVAIS


El transporte marítimo es crucial para la economía global, pero enfrenta desafíos significativos debido a actividades fraudulentas, como la falsificación de datos de posicionamiento de los buques. Aunque la tecnología AIS (Automatic Identification System) es vital para monitorear y gestionar el tráfico marítimo, su fiabilidad no siempre está garantizada, lo que pone en riesgo la seguridad y la gestión eficiente de los recursos.

Este proyecto propone técnicas de validación y verificación de datos AIS mediante una interfaz web interactiva y personalizable. Esta herramienta visual y eficaz ayudará a los organismos de control marítimo a detectar y prevenir actividades anómalas, fortaleciendo la seguridad, integridad, eficiencia y transparencia en la gestión del transporte marítimo global.

![Screenshot 2024-07-23 112853](https://github.com/user-attachments/assets/cfaba239-1e37-4cef-8763-3dcd5c6ac478)

## Servidor Web

El proyecto ofrece una interfaz web interactiva y adaptable a cualquier dispositivo para la vigilancia y filtrado de información sobre embarcaciones detectadas y su verificación posicional. Esto se realiza mediante un sistema de radiogoniometría que proporciona ángulos de incidencia de las señales, utilizados en un algoritmo de triangulación para calcular una elipse de confianza del 95%, identificando posiciones fraudulentas y notificando al usuario.

La aplicación web tiene dos modos de funcionamiento: Vigilancia, para monitoreo en tiempo real, y Simulacro, para entrenar a operarios en situaciones predefinidas. También permite consultar el historial de cada embarcación para detectar rutas anómalas y alertar al usuario. Además, se pueden decodificar y visualizar mensajes AIS pregrabados.

El acceso a las funcionalidades se controla mediante tres roles: Base (solo modo Vigilancia), Operarios (acceso total) y Administradores (acceso y modificación de la base de datos). Para proteger la información sensible, se implementó un sistema de reconocimiento facial como verificación en dos pasos.

![Screenshot 2024-07-23 113103](https://github.com/user-attachments/assets/6f370a3d-7080-4202-bf78-8b2755dafef0)

![Screenshot 2024-07-23 113131](https://github.com/user-attachments/assets/84ef45c2-2e17-4aea-8ebb-870adc8163bf)

## Receptor y Decodificador AIS

El sistema incluye un nodo receptor ubicado en la costa, compuesto por una Raspberry Pi conectada a una radio definida por software (SDR), que captura señales de radio AIS, las decodifica y las transmite al servidor mediante un enlace LTE.

La implementación del decodificador se realizó en dos fases: primero, se desarrolló un programa en Matlab y se probaron señales AIS pregrabadas; luego, se implementó el algoritmo en Python, verificando las salidas de ambos programas para asegurar su correcto funcionamiento.

![Screenshot 2024-07-23 113455](https://github.com/user-attachments/assets/3c21f029-2b84-4c31-94ca-cd23779ec325)


Un sistema AIS transmite datos del buque mediante un emisor VHF, usando los canales 87B y 88B (frecuencias 161.975 MHz y 162.025 MHz) con modulación GMSK de 9.6 kbits/s en canales de 25kHz, usando un protocolo HDLC. La estructura y tipos de mensajes de AIS siguen la Recomendación UIT-R M.1371-5 (02/2014).

![Screenshot 2024-07-23 113542](https://github.com/user-attachments/assets/6c795e29-1dd6-4f24-b980-dae1ca5aa9ec)

## Sistema fotovoltaico de alimentación

![Screenshot 2024-07-23 114000](https://github.com/user-attachments/assets/5234c594-bf43-47fe-8456-42bff88d7c4c)


El esquema consta de cuatro componentes principales:

- Panel Solar: Captura la energía solar disponible y la convierte en electricidad.
- Controlador de Carga: Regula el flujo de energía hacia la Raspberry Pi o una batería recargable, asegurando una carga óptima y segura sin comprometer la autonomía de la Raspberry.
- Batería Recargable: Almacena la energía cuando no se utiliza directamente.
- Convertidor Reductor: Ajusta la tensión de salida del controlador de carga a niveles adecuados para alimentar la Raspberry Pi.

![1000022877](https://github.com/user-attachments/assets/586d95e0-c5e9-4451-b95f-b4001f84520b)

Tecnologías

![Screenshot 2024-07-23 114113](https://github.com/user-attachments/assets/6096bb5f-ea02-41ca-a8c7-a6a3b40ecb73)
