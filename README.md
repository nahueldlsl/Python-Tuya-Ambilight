# AmbiTuya: Controlador de Iluminación Ambiental Inteligente

Crea un sistema de iluminación ambiental (Ambilight) inmersivo y en tiempo real utilizando una tira de luces LED inteligente (compatible con Tuya/Smart Life) y el poder de Python.

Este proyecto va más allá de un simple promedio de color. Utiliza algoritmos de machine learning para analizar de forma inteligente el contenido de tu pantalla, seleccionando los colores más vibrantes y representativos de la escena. El resultado es una experiencia de iluminación ambiental que reacciona de forma dinámica y artística a tus películas y videojuegos, aumentando drásticamente la inmersión.

# ✨ Características Principales

Análisis de Color Vívido: En lugar de promediar la pantalla (lo que a menudo resulta en colores grises o marrones), el script utiliza un algoritmo K-Means optimizado para identificar los colores clave y priorizar aquellos con mayor saturación y relevancia en la escena.

Brillo Dinámico y Adaptativo: La intensidad de la luz se mapea de forma inteligente al brillo general de la pantalla. Las escenas oscuras producen una luz tenue y sutil, mientras que las escenas brillantes iluminan la habitación, con un apagado automático en negros casi absolutos.

Transiciones Inteligentes: El sistema diferencia entre cambios de plano y movimiento dentro de una escena. Ofrece transiciones suaves y fluidas para un movimiento normal y cortes de color instantáneos para cambios de escena abruptos, eliminando el parpadeo molesto.

Perfiles Preconfigurados: Viene con perfiles "cinematic" y "action" listos para usar, con configuraciones optimizadas para películas (suave y atmosférico) y para videojuegos (rápido y vibrante).

Altamente Configurable: Todos los parámetros, desde las credenciales del dispositivo hasta la sensibilidad del algoritmo, se gestionan desde un archivo config.json fácil de editar.

Control 100% Local: Toda la comunicación con la tira LED se realiza en tu red local, asegurando la respuesta más rápida posible (baja latencia) sin depender de servidores en la nube.

# 🚀 Puesta en Marcha

Sigue estos pasos para poner en funcionamiento el sistema en tu computadora.

**1. Prerrequisitos**

Python 3.6 o superior.

Una tira de luces LED compatible con la plataforma Tuya / Smart Life, ya configurada en la app de tu móvil.

Haber obtenido tu Device ID, IP Local y Local Key.

**2. Instalación**

Clona o descarga este repositorio en tu computadora. Luego, instala las dependencias necesarias.

**3. Configuración**

Busca el archivo ```config.example.json``` y haz una copia del mismo.

Renombra la copia a ```config.json```

Abre ```config.json``` y rellena los datos de tu dispositivo en la sección device_settings: device_id, device_ip y local_key.

Elige tu perfil inicial cambiando el valor de active_profile a "cinematic" o "action".

**4. Ejecución**

Ejecuta el script principal desde tu terminal:

```python messi.py```
¡Y a disfrutar! La luz debería empezar a reaccionar a tu pantalla.

# 🛠️ Ajustes y Configuración

Puedes personalizar finamente la experiencia editando el archivo config.json:

active_profile: Cambia entre "cinematic" y "action" para adaptar el comportamiento de la luz.

saturation_factor: Aumenta este valor para colores más intensos (ej. 1.8) o redúcelo para un efecto más sutil (ej. 1.2).

min_brightness_pc: El brillo mínimo que tendrá la luz en escenas oscuras (antes de apagarse por completo).

scene_cut_color_distance: El umbral para detectar un corte de escena. Un número más bajo hará que las transiciones instantáneas sean más frecuentes.

# 💻 Tecnologías Utilizadas

Python 3

tinytuya: Para la comunicación local con el dispositivo.

scikit-learn: Para el análisis de color mediante MiniBatchKMeans.

Pillow: Para la manipulación y redimensionado de imágenes.

mss: Para una captura de pantalla ultrarrápida y de bajo nivel.
