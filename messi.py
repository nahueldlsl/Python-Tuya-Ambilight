import tinytuya
import mss
import time
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import colorsys
import json

# --- 1. CARGAMOS LA CONFIGURACIÓN Y EL PERFIL ACTIVO ---
try:
    with open('config.json') as f:
        config = json.load(f)
    
    active_profile_name = config.get('active_profile', 'cinematic')
    profile = config['profiles'][active_profile_name]
    print(f"--- Cargando perfil: '{active_profile_name}' ---")

except (FileNotFoundError, KeyError) as e:
    print(f"ERROR: No se pudo cargar la configuración o el perfil. Revisa 'config.json'. Error: {e}")
    exit()

# Extraemos las configuraciones del perfil activo
DEVICE_ID = config['device_settings']['device_id']
DEVICE_IP = config['device_settings']['device_ip']
LOCAL_KEY = config['device_settings']['local_key']
ANALYSIS_WIDTH, ANALYSIS_HEIGHT = profile['analysis_width'], profile['analysis_height']
NUM_COLORS_TO_FIND = profile['num_colors_to_find']
SATURATION_FACTOR = profile['saturation_factor']
TRANSITION_STEPS, TRANSITION_DELAY = profile['transition_steps'], profile['transition_delay']
MIN_BRIGHTNESS_PC, MAX_BRIGHTNESS_PC = profile['min_brightness_pc'], profile['max_brightness_pc']
OFF_THRESHOLD = profile['off_threshold']
BRIGHTNESS_JUMP_THRESHOLD = profile['brightness_jump_threshold']

# --- CONEXIÓN CON EL DISPOSITIVO ---
try:
    device = tinytuya.BulbDevice(DEVICE_ID, DEVICE_IP, LOCAL_KEY)
    device.set_version(3.3)
    print("¡Dispositivo Tuya conectado!")
except Exception as e:
    print(f"Error al conectar con el dispositivo Tuya: {e}")
    exit()

# --- FUNCIONES AUXILIARES ---

# ESTA ES LA FUNCIÓN QUE FALTABA
def map_value(value, from_min, from_max, to_min, to_max):
    """Mapea un valor de un rango a otro (interpolación lineal)."""
    if from_max == from_min:
        return to_min
    return to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min)

def get_color_properties(r, g, b):
    """Devuelve el brillo y la saturación de un color."""
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    brightness = l * 255
    saturation = s
    return brightness, saturation

def boost_saturation(r, g, b, factor):
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    s = min(1.0, s * factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return int(r*255), int(g*255), int(b*255)

def get_vibrant_color(image):
    """Algoritmo de 'Color Vívido'."""
    pixels = np.array(image).reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=NUM_COLORS_TO_FIND, n_init='auto', random_state=0).fit(pixels)
    
    best_color = None
    max_score = -1

    for i, color in enumerate(kmeans.cluster_centers_):
        r, g, b = color.astype(int)
        pixel_count = np.count_nonzero(kmeans.labels_ == i)
        brightness, saturation = get_color_properties(r, g, b)
        
        if brightness < 15 or brightness > 240 or saturation < 0.15:
            continue
            
        score = pixel_count * (saturation ** 2)

        if score > max_score:
            max_score = score
            best_color = color.astype(int)
            
    if best_color is None:
        dominant_cluster_index = np.argmax(np.unique(kmeans.labels_, return_counts=True)[1])
        best_color = kmeans.cluster_centers_[dominant_cluster_index].astype(int)
        
    return best_color

# --- BUCLE PRINCIPAL ---
try:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        last_rgb = np.array([0, 0, 0])
        last_brightness = 0
        is_on = False
        bulb_brightness = 0 # Inicializamos la variable

        while True:
            sct_img = sct.grab(monitor)
            pil_img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            img_resized = pil_img.resize((ANALYSIS_WIDTH, ANALYSIS_HEIGHT))
            
            target_rgb = get_vibrant_color(img_resized)
            target_brightness, _ = get_color_properties(target_rgb[0], target_rgb[1], target_rgb[2])

            if target_brightness < OFF_THRESHOLD:
                if is_on: device.turn_off(); is_on = False
                target_rgb = np.array([0, 0, 0])
            else:
                if not is_on: device.turn_on(); is_on = True
                bulb_brightness = map_value(target_brightness, 0, 255, MIN_BRIGHTNESS_PC, MAX_BRIGHTNESS_PC)
                device.set_brightness_percentage(round(bulb_brightness))
                r, g, b = boost_saturation(target_rgb[0], target_rgb[1], target_rgb[2], SATURATION_FACTOR)
                target_rgb = np.array([r, g, b])
            
            print(f"Color: {target_rgb} | Brillo Pantalla: {target_brightness:.0f} | Brillo Bombilla: {bulb_brightness if is_on else 0:.0f}%")

            brightness_jump = target_brightness - last_brightness
            if is_on and brightness_jump > BRIGHTNESS_JUMP_THRESHOLD and TRANSITION_STEPS > 0:
                print(f"¡FLASH DETECTADO!")
                device.set_colour(target_rgb[0], target_rgb[1], target_rgb[2])
                time.sleep(0.05)
            else:
                diff_rgb = target_rgb - last_rgb
                for i in range(1, TRANSITION_STEPS + 1):
                    step_rgb = last_rgb + (diff_rgb * i / TRANSITION_STEPS)
                    r_step, g_step, b_step = step_rgb.astype(int)
                    if is_on: device.set_colour(r_step, g_step, b_step)
                    if TRANSITION_DELAY > 0: time.sleep(TRANSITION_DELAY)
            
            last_rgb = target_rgb
            last_brightness = target_brightness
            
except KeyboardInterrupt:
    print("\nPrograma terminado.")
    if is_on: device.turn_off()
except Exception as e:
    print(f"Ocurrió un error: {e}")