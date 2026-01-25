import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import datetime
import random
import os

# ==========================================
# 1. LÓGICA DE BLOQUEO (BIBLIOTECA)
# ==========================================
class FairRWLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.readers = 0
        self.writing = False
        self.writers_waiting = 0

    def acquire_read(self):
        with self.condition:
            # Un lector espera si hay alguien escribiendo O si hay escritores en fila
            while self.writing or self.writers_waiting > 0:
                self.condition.wait()
            self.readers += 1

    def release_read(self):
        with self.condition:
            self.readers -= 1
            if self.readers == 0:
                self.condition.notify_all()

    def acquire_write(self):
        with self.condition:
            self.writers_waiting += 1
            # El escritor espera hasta que no haya NADIE dentro
            while self.writing or self.readers > 0:
                self.condition.wait()
            self.writers_waiting -= 1
            self.writing = True

    def release_write(self):
        with self.condition:
            self.writing = False
            self.condition.notify_all()

# ==========================================
# 2. INTERFAZ GRÁFICA INTEGRADA
# ==========================================
class AppConcurrencia:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Bloqueo Justo de Archivos")
        self.root.geometry("700x650")
        self.rw_lock = FairRWLock()
        self.file_name = "archivo_critico.txt"
        
        # Limpiar archivo al iniciar
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

        # UI Elements
        tk.Label(root, text="Monitor de Sección Crítica", font=("Arial", 16, "bold")).pack(pady=10)

        # Espacio de visualización (Canvas)
        self.canvas = tk.Canvas(root, width=600, height=200, bg="#ecf0f1", highlightthickness=2, highlightbackground="#bdc3c7")
        self.canvas.pack(pady=10)
        # Rectángulo que representa el archivo
        self.canvas.create_rectangle(150, 40, 450, 160, outline="#7f8c8d", width=2, dash=(5, 2))
        self.canvas.create_text(300, 20, text="ARCHIVO (Sección Crítica)", font=("Arial", 10, "bold"), fill="#7f8c8d")
        
        # Consola de Log
        tk.Label(root, text="Eventos del Sistema:", font=("Arial", 10, "bold")).pack(anchor="w", padx=50)
        self.log_area = scrolledtext.ScrolledText(root, width=75, height=12, bg="#2c3e50", fg="#ecf0f1", font=("Consolas", 9))
        self.log_area.pack(padx=10, pady=5)

        # Botones
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="+ Añadir Lector", bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  command=self.spawn_reader, width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="+ Añadir Escritor", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                  command=self.spawn_writer, width=15).pack(side=tk.LEFT, padx=10)

    # --- Herramientas Visuales ---
    def draw_thread(self, id, type):
        """Dibuja el hilo dentro del archivo en el Canvas."""
        color = "#3498db" if type == "R" else "#e74c3c"
        # Posiciones aleatorias dentro de la zona del archivo (rectángulo 150-450, 40-160)
        x = random.randint(170, 410)
        y = random.randint(60, 130)
        
        tag = f"hilo_{id}"
        self.canvas.create_oval(x, y, x+25, y+25, fill=color, outline="white", tags=tag, width=2)
        self.canvas.create_text(x+12, y+12, text=f"{type}{id}", fill="white", font=("Arial", 7, "bold"), tags=tag)
        return tag

    def write_log(self, text, tag_color=None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {text}\n", tag_color)
        self.log_area.see(tk.END)

    # --- Procesos de los Hilos ---
    def reader_task(self, id):
        self.write_log(f"Lector {id}: Esperando turno...")
        
        # 1. ACQUIRE (Bajo nivel)
        self.rw_lock.acquire_read()
        
        # 2. ENTRADA VISUAL
        tag = self.draw_thread(id, "R")
        
        try:
            # Operación de archivo
            with open(self.file_name, "r") as f:
                content = f.readlines()
                last = content[-1].strip() if content else "Archivo vacío"
            self.write_log(f"-> Lector {id} LEYENDO: {last}")
            time.sleep(random.uniform(2, 4)) # Tiempo en sección crítica
        except Exception as e:
            self.write_log(f"Error Lector: {e}")
        finally:
            # 3. SALIDA VISUAL
            self.canvas.delete(tag)
            # 4. RELEASE (Bajo nivel)
            self.rw_lock.release_read()
            self.write_log(f"<- Lector {id} salió.")

    def writer_task(self, id):
        self.write_log(f"ESCRITOR {id}: SOLICITANDO EXCLUSIVIDAD...", "warning")
        
        # 1. ACQUIRE (Bajo nivel)
        self.rw_lock.acquire_write()
        
        # 2. ENTRADA VISUAL
        tag = self.draw_thread(id, "W")
        
        try:
            self.write_log(f"!!! ESCRITOR {id} ESCRIBIENDO !!!", "warning")
            with open(self.file_name, "a") as f:
                ahora = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"Modificado por Escritor {id} a las {ahora}\n")
            time.sleep(3) # Tiempo en sección crítica
        except Exception as e:
            self.write_log(f"Error Escritor: {e}")
        finally:
            # 3. SALIDA VISUAL
            self.canvas.delete(tag)
            # 4. RELEASE (Bajo nivel)
            self.rw_lock.release_write()
            self.write_log(f"!!! ESCRITOR {id} liberó el archivo.")

    # --- Lanzadores ---
    def spawn_reader(self):
        r_id = random.randint(100, 999)
        threading.Thread(target=self.reader_task, args=(r_id,), daemon=True).start()

    def spawn_writer(self):
        w_id = random.randint(10, 99)
        threading.Thread(target=self.writer_task, args=(w_id,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    # Configuración de colores de texto para el log
    app = AppConcurrencia(root)
    app.log_area.tag_config("warning", foreground="#f39c12")
    root.mainloop()