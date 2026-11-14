import pygame
import math
import random
import array

# --- INICIALIZACIÓN ---
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_DISPONIBLE = True
except Exception as e:
    print("Aviso: Audio no disponible, el juego funcionará sin sonido.", e)
    AUDIO_DISPONIBLE = False

ANCHO, ALTO = 1100, 720
# PANTALLA EN PANTALLA COMPLETA CON AUTO-ESCALADO
PANTALLA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Turbo Rivals 2P - Carrera Arcade")
RELOJ = pygame.time.Clock()

# --- FUENTES ---
FUENTE_TITULO = pygame.font.SysFont("arial", 64, bold=True)
FUENTE_SUB = pygame.font.SysFont("arial", 28, bold=True)
FUENTE_BOTON = pygame.font.SysFont("arial", 24, bold=True)
FUENTE_HUD = pygame.font.SysFont("consolas", 20, bold=True)

# --- COLORES ---
BLANCO = (255, 255, 255)
NEGRO = (15, 15, 20)
GRIS_OSCURO = (35, 38, 45)
GRIS_CLARO = (180, 185, 195)
ROJO = (235, 55, 55)
AZUL = (45, 135, 245)
VERDE = (46, 204, 113)
AMARILLO = (241, 196, 15)
CIAN = (0, 230, 230)
NARANJA = (243, 156, 18)

# --- GENERADOR DE SONIDOS PROCEDURALES ---
class SistemaSonido:
    def __init__(self):
        self.activo = True
        if AUDIO_DISPONIBLE:
            try:
                self.sonido_click = self._generar_tono(600, 0.08, 0.3)
                self.sonido_poder = self._generar_arpegio([523, 659, 784, 1046], 0.06, 0.3)
                self.sonido_choque = self._generar_ruido(0.2, 0.35)
                self.sonido_meta = self._generar_arpegio([440, 554, 659, 880], 0.12, 0.4)
            except Exception:
                self.activo = False
        else:
            self.activo = False

    def _generar_tono(self, freq, duracion, vol):
        sample_rate = 22050
        n_samples = int(sample_rate * duracion)
        buf = array.array('h')
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(vol * 32767.0 * math.sin(2.0 * math.pi * freq * t) * (1 - i / n_samples))
            buf.append(val)
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def _generar_arpegio(self, freqs, dur_nota, vol):
        sample_rate = 22050
        buf = array.array('h')
        for freq in freqs:
            n_samples = int(sample_rate * dur_nota)
            for i in range(n_samples):
                t = float(i) / sample_rate
                val = int(vol * 32767.0 * math.sin(2.0 * math.pi * freq * t))
                buf.append(val)
                buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def _generar_ruido(self, duracion, vol):
        sample_rate = 22050
        n_samples = int(sample_rate * duracion)
        buf = array.array('h')
        for i in range(n_samples):
            val = int(vol * 32767.0 * random.uniform(-1, 1) * (1 - i / n_samples))
            buf.append(val)
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def reproducir(self, sonido):
        if self.activo and AUDIO_DISPONIBLE and hasattr(self, 'sonido_click'):
            try:
                sonido.play()
            except Exception:
                pass

SONIDOS = SistemaSonido()

# --- DEFINICIÓN DE MAPAS ---
MAPAS = [
    {
        "nombre": "Circuito Clásico",
        "fondo": (38, 125, 48),
        "pista": (55, 58, 64),
        "borde1": (220, 40, 40),
        "borde2": (240, 240, 240),
        "obstaculo_color": (30, 30, 35),
        "rect_exterior": pygame.Rect(90, 95, 920, 560),
        "rect_interior": pygame.Rect(270, 255, 560, 240),
        "obstaculos": [
            pygame.Rect(480, 120, 35, 35),
            pygame.Rect(700, 180, 40, 40),
            pygame.Rect(880, 360, 40, 40),
            pygame.Rect(550, 530, 45, 45),
            pygame.Rect(280, 570, 35, 35),
            pygame.Rect(140, 320, 40, 40),
        ],
        "cajas_poder": [(380, 175), (820, 175), (920, 480), (450, 575), (180, 430)]
    },
    {
        "nombre": "Desierto del Cañón",
        "fondo": (210, 150, 85),
        "pista": (150, 105, 65),
        "borde1": (230, 180, 50),
        "borde2": (120, 70, 30),
        "obstaculo_color": (110, 75, 50),
        "rect_exterior": pygame.Rect(80, 90, 940, 570),
        "rect_interior": pygame.Rect(250, 240, 600, 270),
        "obstaculos": [
            pygame.Rect(350, 115, 45, 45),
            pygame.Rect(620, 165, 45, 45),
            pygame.Rect(910, 280, 45, 45),
            pygame.Rect(750, 550, 50, 50),
            pygame.Rect(380, 540, 45, 45),
            pygame.Rect(120, 420, 45, 45),
        ],
        "cajas_poder": [(500, 165), (930, 420), (550, 580), (165, 250)]
    },
    {
        "nombre": "Pista Ártica",
        "fondo": (225, 240, 250),
        "pista": (135, 175, 205),
        "borde1": (40, 140, 220),
        "borde2": (255, 255, 255),
        "obstaculo_color": (80, 190, 240),
        "rect_exterior": pygame.Rect(95, 95, 910, 560),
        "rect_interior": pygame.Rect(280, 260, 540, 230),
        "obstaculos": [
            pygame.Rect(420, 130, 40, 40),
            pygame.Rect(680, 130, 40, 40),
            pygame.Rect(870, 380, 45, 45),
            pygame.Rect(630, 540, 45, 45),
            pygame.Rect(340, 520, 40, 40),
            pygame.Rect(150, 260, 40, 40),
        ],
        "cajas_poder": [(550, 175), (910, 240), (490, 575), (185, 480)]
    }
]

# --- CLASE BOTÓN UI ---
class Boton:
    def __init__(self, x, y, w, h, texto, color_base=GRIS_OSCURO, color_hover=(65, 70, 82)):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover

    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos)
        color = self.color_hover if hover else self.color_base

        pygame.draw.rect(superficie, (10, 10, 15), self.rect.move(3, 3), border_radius=8)
        pygame.draw.rect(superficie, color, self.rect, border_radius=8)
        pygame.draw.rect(superficie, BLANCO if hover else GRIS_CLARO, self.rect, 2, border_radius=8)

        txt_surf = FUENTE_BOTON.render(self.texto, True, BLANCO)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        superficie.blit(txt_surf, txt_rect)

    def fue_clickeado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                SONIDOS.reproducir(SONIDOS.sonido_click)
                return True
        return False

# --- CLASE PARTÍCULA ---
class Particula:
    def __init__(self, x, y, color, vida=20, tam=5):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.color = color
        self.vida = vida
        self.vida_max = vida
        self.tam = tam

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    def dibujar(self, superficie):
        if self.vida > 0:
            radio = max(1, int(self.tam * (self.vida / self.vida_max)))
            pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), radio)

# --- CLASE AUTO (JUGADOR) ---
class Auto:
    def __init__(self, x, y, color, nombre, controles):
        self.x_inicial = x
        self.y_inicial = y
        self.color = color
        self.nombre = nombre
        self.controles = controles
        self.reiniciar()

    def reiniciar(self):
        self.x = float(self.x_inicial)
        self.y = float(self.y_inicial)
        self.angulo = 0.0
        self.velocidad = 0.0
        self.vel_max_base = 5.4
        self.aceleracion = 0.22
        self.friccion = 0.06
        self.giro_vel = 4.2

        self.vueltas = 0
        self.checkpoint_pasado = False
        self.invulnerable_choque = 0

        self.poder_actual = None
        self.tiempo_turbo = 0
        self.escudo_activo = False
        self.tiempo_congelado = 0

    def actualizar(self, teclas, mapa, otro_auto, particulas):
        if self.invulnerable_choque > 0:
            self.invulnerable_choque -= 1
        if self.tiempo_turbo > 0:
            self.tiempo_turbo -= 1
        if self.tiempo_congelado > 0:
            self.tiempo_congelado -= 1

        if teclas[self.controles["poder"]] and self.poder_actual:
            self._activar_poder(otro_auto)

        en_pista = self._esta_en_pista(mapa)
        vel_max = self.vel_max_base
        if not en_pista:
            vel_max *= 0.52
        if self.tiempo_turbo > 0:
            vel_max *= 1.55
        if self.tiempo_congelado > 0:
            vel_max *= 0.45

        if teclas[self.controles["arriba"]]:
            self.velocidad += self.aceleracion * (1.5 if self.tiempo_turbo > 0 else 1.0)
        elif teclas[self.controles["abajo"]]:
            self.velocidad -= self.aceleracion * 0.8
        else:
            if self.velocidad > 0:
                self.velocidad = max(0, self.velocidad - self.friccion)
            elif self.velocidad < 0:
                self.velocidad = min(0, self.velocidad + self.friccion)

        self.velocidad = max(-vel_max * 0.5, min(vel_max, self.velocidad))

        if abs(self.velocidad) > 0.2:
            factor_dir = 1 if self.velocidad > 0 else -1
            if teclas[self.controles["izquierda"]]:
                self.angulo -= self.giro_vel * factor_dir
            if teclas[self.controles["derecha"]]:
                self.angulo += self.giro_vel * factor_dir

        rad = math.radians(self.angulo)
        nx = self.x + math.cos(rad) * self.velocidad
        ny = self.y + math.sin(rad) * self.velocidad

        nx = max(25, min(ANCHO - 25, nx))
        ny = max(75, min(ALTO - 25, ny))

        rect_auto = pygame.Rect(nx - 14, ny - 14, 28, 28)
        if rect_auto.colliderect(mapa["rect_interior"]):
            self.velocidad *= -0.4
        else:
            self.x = nx
            self.y = ny

        if self.tiempo_turbo > 0 and random.random() < 0.8:
            ex = self.x - math.cos(rad) * 20
            ey = self.y - math.sin(rad) * 20
            particulas.append(Particula(ex, ey, random.choice([NARANJA, AMARILLO, ROJO]), 15, 6))
        elif abs(self.velocidad) > 3.5 and random.random() < 0.35:
            ex = self.x - math.cos(rad) * 18
            ey = self.y - math.sin(rad) * 18
            color_humo = (200, 200, 200) if en_pista else mapa["fondo"]
            particulas.append(Particula(ex, ey, color_humo, 18, 4))

        rect_auto = pygame.Rect(self.x - 14, self.y - 14, 28, 28)
        for obs in mapa["obstaculos"]:
            if rect_auto.colliderect(obs) and self.invulnerable_choque == 0:
                if self.escudo_activo:
                    self.escudo_activo = False
                    self.invulnerable_choque = 45
                    SONIDOS.reproducir(SONIDOS.sonido_click)
                else:
                    self.velocidad *= 0.25
                    self.invulnerable_choque = 50
                    SONIDOS.reproducir(SONIDOS.sonido_choque)
                    for _ in range(12):
                        particulas.append(Particula(self.x, self.y, NARANJA, 20, 5))

        if self.y > 420 and 450 < self.x < 650:
            self.checkpoint_pasado = True

        if self.checkpoint_pasado and self.y < 260 and 540 <= self.x <= 570:
            self.vueltas += 1
            self.checkpoint_pasado = False
            SONIDOS.reproducir(SONIDOS.sonido_meta)
            for _ in range(20):
                particulas.append(Particula(self.x, self.y, AMARILLO, 25, 6))

    def _activar_poder(self, otro_auto):
        if self.poder_actual == "TURBO":
            self.tiempo_turbo = 130
        elif self.poder_actual == "ESCUDO":
            self.escudo_activo = True
        elif self.poder_actual == "CONGELAR":
            otro_auto.tiempo_congelado = 140
        SONIDOS.reproducir(SONIDOS.sonido_poder)
        self.poder_actual = None

    def _esta_en_pista(self, mapa):
        p = (int(self.x), int(self.y))
        return mapa["rect_exterior"].collidepoint(p) and not mapa["rect_interior"].collidepoint(p)

    def dibujar(self, superficie):
        w, h = 42, 24
        surf_auto = pygame.Surface((w, h), pygame.SRCALPHA)

        pygame.draw.rect(surf_auto, NEGRO, (6, 0, 10, 4), border_radius=2)
        pygame.draw.rect(surf_auto, NEGRO, (26, 0, 10, 4), border_radius=2)
        pygame.draw.rect(surf_auto, NEGRO, (6, h - 4, 10, 4), border_radius=2)
        pygame.draw.rect(surf_auto, NEGRO, (26, h - 4, 10, 4), border_radius=2)

        color_cuerpo = CIAN if self.tiempo_congelado > 0 else self.color
        pygame.draw.rect(surf_auto, color_cuerpo, (3, 3, w - 6, h - 6), border_radius=6)
        pygame.draw.rect(surf_auto, BLANCO, (8, h // 2 - 2, w - 16, 4))
        pygame.draw.polygon(surf_auto, (25, 30, 40), [(22, 5), (31, 7), (31, h - 7), (22, h - 5)])
        pygame.draw.rect(surf_auto, (20, 20, 25), (2, 4, 4, h - 8))

        rotado = pygame.transform.rotate(surf_auto, -self.angulo)
        rect = rotado.get_rect(center=(int(self.x), int(self.y)))
        superficie.blit(rotado, rect)

        if self.escudo_activo:
            pygame.draw.circle(superficie, CIAN, (int(self.x), int(self.y)), 28, 3)

# --- CLASE CAJA DE PODER ---
class CajaPoder:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)
        self.cooldown = 0
        self.pulso = random.uniform(0, 6.28)

    def actualizar(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        self.pulso += 0.1

    def dibujar(self, superficie):
        if self.cooldown == 0:
            offset = math.sin(self.pulso) * 3
            r = self.rect.move(0, int(offset))
            pygame.draw.rect(superficie, AMARILLO, r, border_radius=6)
            pygame.draw.rect(superficie, BLANCO, r, 2, border_radius=6)
            txt = FUENTE_HUD.render("?", True, NEGRO)
            superficie.blit(txt, txt.get_rect(center=r.center))

# --- DIBUJADO DE PISTA ---
def dibujar_mapa(superficie, mapa):
    superficie.fill(mapa["fondo"])

    ext = mapa["rect_exterior"]
    inte = mapa["rect_interior"]

    pygame.draw.rect(superficie, mapa["borde1"], ext.inflate(16, 16), border_radius=36)
    pygame.draw.rect(superficie, mapa["borde2"], ext.inflate(16, 16), 4, border_radius=36)
    pygame.draw.rect(superficie, mapa["pista"], ext, border_radius=28)

    centro_rect = ext.inflate(-170, -160)
    pygame.draw.rect(superficie, (200, 210, 220), centro_rect, 2, border_radius=20)

    pygame.draw.rect(superficie, mapa["borde1"], inte.inflate(14, 14), border_radius=24)
    pygame.draw.rect(superficie, mapa["fondo"], inte, border_radius=20)

    meta_x = 550
    meta_y_inicio = ext.top
    meta_y_fin = inte.top
    tam_cuadro = 12
    filas = (meta_y_fin - meta_y_inicio) // tam_cuadro
    for f in range(filas):
        for c in range(2):
            color = BLANCO if (f + c) % 2 == 0 else NEGRO
            pygame.draw.rect(superficie, color, (meta_x + c * tam_cuadro, meta_y_inicio + f * tam_cuadro, tam_cuadro, tam_cuadro))

    for obs in mapa["obstaculos"]:
        pygame.draw.ellipse(superficie, mapa["obstaculo_color"], obs)
        pygame.draw.ellipse(superficie, NEGRO, obs, 2)

# --- BUCLE PRINCIPAL ---
def main():
    estado = "MENU"
    mapa_idx = 0
    vueltas_objetivo = 3
    ganador = None

    btn_jugar = Boton(ANCHO // 2 - 140, 260, 280, 55, "JUGAR", VERDE, (39, 174, 96))
    btn_mapa = Boton(ANCHO // 2 - 140, 335, 280, 55, f"MAPA: {MAPAS[mapa_idx]['nombre']}")
    btn_sonido_menu = Boton(ANCHO // 2 - 140, 410, 280, 55, "SONIDO: ON" if SONIDOS.activo else "SONIDO: OFF")
    btn_salir_menu = Boton(ANCHO // 2 - 140, 485, 280, 55, "SALIR", ROJO, (192, 57, 43))

    btn_menu_hud = Boton(15, 12, 110, 40, "MENÚ")
    btn_reiniciar_hud = Boton(135, 12, 135, 40, "REINICIAR")
    btn_sonido_hud = Boton(ANCHO - 265, 12, 145, 40, "SONIDO: ON" if SONIDOS.activo else "SONIDO: OFF")
    btn_salir_hud = Boton(ANCHO - 110, 12, 95, 40, "SALIR", ROJO, (192, 57, 43))

    btn_revancha = Boton(ANCHO // 2 - 140, 390, 280, 55, "REINICIAR", VERDE, (39, 174, 96))
    btn_volver_menu = Boton(ANCHO // 2 - 140, 465, 280, 55, "MENÚ")

    controles_j1 = {
        "arriba": pygame.K_w,
        "abajo": pygame.K_s,
        "izquierda": pygame.K_a,
        "derecha": pygame.K_d,
        "poder": pygame.K_SPACE
    }
    controles_j2 = {
        "arriba": pygame.K_UP,
        "abajo": pygame.K_DOWN,
        "izquierda": pygame.K_LEFT,
        "derecha": pygame.K_RIGHT,
        "poder": pygame.K_RETURN
    }

    j1 = Auto(510, 150, ROJO, "JUGADOR 1", controles_j1)
    j2 = Auto(510, 205, AZUL, "JUGADOR 2", controles_j2)
    cajas_poder = []
    particulas = []

    def iniciar_carrera():
        nonlocal cajas_poder, particulas, ganador
        j1.reiniciar()
        j2.reiniciar()
        particulas = []
        ganador = None
        cajas_poder = [CajaPoder(x, y) for (x, y) in MAPAS[mapa_idx]["cajas_poder"]]

    ejecutando = True
    while ejecutando:
        RELOJ.tick(60)
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False  # Salir con la tecla ESC

            if estado == "MENU":
                if btn_jugar.fue_clickeado(evento):
                    iniciar_carrera()
                    estado = "CARRERA"
                elif btn_mapa.fue_clickeado(evento):
                    mapa_idx = (mapa_idx + 1) % len(MAPAS)
                    btn_mapa.texto = f"MAPA: {MAPAS[mapa_idx]['nombre']}"
                elif btn_sonido_menu.fue_clickeado(evento):
                    SONIDOS.activo = not SONIDOS.activo
                    etiqueta = "SONIDO: ON" if SONIDOS.activo else "SONIDO: OFF"
                    btn_sonido_menu.texto = etiqueta
                    btn_sonido_hud.texto = etiqueta
                elif btn_salir_menu.fue_clickeado(evento):
                    ejecutando = False

            elif estado == "CARRERA":
                if btn_menu_hud.fue_clickeado(evento):
                    estado = "MENU"
                elif btn_reiniciar_hud.fue_clickeado(evento):
                    iniciar_carrera()
                elif btn_sonido_hud.fue_clickeado(evento):
                    SONIDOS.activo = not SONIDOS.activo
                    etiqueta = "SONIDO: ON" if SONIDOS.activo else "SONIDO: OFF"
                    btn_sonido_menu.texto = etiqueta
                    btn_sonido_hud.texto = etiqueta
                elif btn_salir_hud.fue_clickeado(evento):
                    ejecutando = False

            elif estado == "VICTORIA":
                if btn_revancha.fue_clickeado(evento):
                    iniciar_carrera()
                    estado = "CARRERA"
                elif btn_volver_menu.fue_clickeado(evento):
                    estado = "MENU"

        if estado == "MENU":
            PANTALLA.fill(NEGRO)
            pygame.draw.rect(PANTALLA, GRIS_OSCURO, (60, 60, ANCHO - 120, ALTO - 120), 4, border_radius=20)

            titulo = FUENTE_TITULO.render("TURBO RIVALS 2P", True, AMARILLO)
            PANTALLA.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 145)))

            sub = FUENTE_HUD.render("J1 (Rojo): W A S D + ESPACIO (Poder)   |   J2 (Azul): FLECHAS + ENTER (Poder)", True, GRIS_CLARO)
            PANTALLA.blit(sub, sub.get_rect(center=(ANCHO // 2, 205)))

            btn_jugar.dibujar(PANTALLA)
            btn_mapa.dibujar(PANTALLA)
            btn_sonido_menu.dibujar(PANTALLA)
            btn_salir_menu.dibujar(PANTALLA)

            info_poderes = FUENTE_HUD.render("Poderes: [TURBO] Velocidad extra  |  [ESCUDO] Bloquea choque  |  [CONGELAR] Frena al rival", True, CIAN)
            PANTALLA.blit(info_poderes, info_poderes.get_rect(center=(ANCHO // 2, 600)))

        elif estado == "CARRERA":
            mapa_actual = MAPAS[mapa_idx]
            dibujar_mapa(PANTALLA, mapa_actual)

            for caja in cajas_poder:
                caja.actualizar()
                caja.dibujar(PANTALLA)
                if caja.cooldown == 0:
                    for jugador in (j1, j2):
                        if caja.rect.collidepoint(jugador.x, jugador.y) and jugador.poder_actual is None:
                            jugador.poder_actual = random.choice(["TURBO", "ESCUDO", "CONGELAR"])
                            caja.cooldown = 240
                            SONIDOS.reproducir(SONIDOS.sonido_poder)

            j1.actualizar(teclas, mapa_actual, j2, particulas)
            j2.actualizar(teclas, mapa_actual, j1, particulas)

            for p in particulas[:]:
                p.actualizar()
                p.dibujar(PANTALLA)
                if p.vida <= 0:
                    particulas.remove(p)

            j1.dibujar(PANTALLA)
            j2.dibujar(PANTALLA)

            if j1.vueltas >= vueltas_objetivo:
                ganador = "JUGADOR 1 (ROJO)"
                estado = "VICTORIA"
            elif j2.vueltas >= vueltas_objetivo:
                ganador = "JUGADOR 2 (AZUL)"
                estado = "VICTORIA"

            pygame.draw.rect(PANTALLA, NEGRO, (0, 0, ANCHO, 64))
            pygame.draw.line(PANTALLA, GRIS_CLARO, (0, 64), (ANCHO, 64), 2)

            btn_menu_hud.dibujar(PANTALLA)
            btn_reiniciar_hud.dibujar(PANTALLA)
            btn_sonido_hud.dibujar(PANTALLA)
            btn_salir_hud.dibujar(PANTALLA)

            p1_poder = j1.poder_actual if j1.poder_actual else "Ninguno"
            p2_poder = j2.poder_actual if j2.poder_actual else "Ninguno"

            hud_j1 = FUENTE_HUD.render(f"J1: Vuelta {j1.vueltas}/{vueltas_objetivo} | Poder: {p1_poder}", True, ROJO)
            hud_j2 = FUENTE_HUD.render(f"J2: Vuelta {j2.vueltas}/{vueltas_objetivo} | Poder: {p2_poder}", True, AZUL)
            PANTALLA.blit(hud_j1, (295, 10))
            PANTALLA.blit(hud_j2, (295, 36))

        elif estado == "VICTORIA":
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            PANTALLA.blit(overlay, (0, 0))

            txt_gana = FUENTE_TITULO.render(f"¡GANA {ganador}!", True, AMARILLO)
            PANTALLA.blit(txt_gana, txt_gana.get_rect(center=(ANCHO // 2, 270)))

            btn_revancha.dibujar(PANTALLA)
            btn_volver_menu.dibujar(PANTALLA)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()