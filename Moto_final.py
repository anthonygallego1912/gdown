import cv2
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# --- CONFIGURACIÓN ---
image_path = "FB_IMG_1759028394292.jpg"  # tu imagen
output_path = "moto_final.mp4"
audio_path = "motor.mp3"
fps = 30
duration = 15
frames = fps * duration

# --- CARGAR IMAGEN ---
img = cv2.imread(image_path)
h, w, _ = img.shape
out_w, out_h = 1280, 720

frames_list = []

for i in range(frames):
    # Paneo lateral
    shift = int((w - out_w) * (i / frames))
    frame = img[0:out_h, shift:shift+out_w].copy()

    # Vibración
    dx = np.random.randint(-2, 3)
    dy = np.random.randint(-2, 3)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    frame = cv2.warpAffine(frame, M, (out_w, out_h))

    # Humo escape inferior derecho
    overlay = frame.copy()
    center_x, center_y = out_w - 150, out_h - 100
    radius = np.random.randint(15, 30)
    cv2.circle(
        overlay,
        (center_x + np.random.randint(-10, 10), center_y - (i % 50)),
        radius,
        (200, 200, 200),
        -1
    )
    frame = cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)

    frames_list.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# Crear clip
clip = ImageSequenceClip(frames_list, fps=fps)

# Añadir audio
audio = AudioFileClip(audio_path)
if audio.duration < duration:
    audio = audio.loop(duration=duration)
clip = clip.set_audio(audio)

# Exportar video
clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

# --- Subida a Google Drive ---
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # abrirá el navegador para que inicies sesión
drive = GoogleDrive(gauth)

file_drive = drive.CreateFile({'title': output_path})
file_drive.SetContentFile(output_path)
file_drive.Upload()

file_drive.InsertPermission({
    'type': 'anyone',
    'value': 'anyone',
    'role': 'reader'
})

print("✅ Video subido a Google Drive")
print("🔗 Link de descarga:", file_drive['alternateLink'])
