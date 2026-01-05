import pyglet
import pyglet.gl as GL
import numpy as np
from pathlib import Path
import click
import os
import random
from math import tan, atan, radians, degrees

from grafica.scenegraph import Scenegraph
import grafica.transformations as tr

"""
El programa muestra el personaje formado por un grafo de escena de la Tarea 2 en una sola pose, pero esta vez implementando el efecto Dolly Zoom. Consiste en modificar la distancia entre la cámara y el personaje y el ángulo de visión de modo que el personaje se vea siempre del mismo tamaño mientras el fondo se acerca o se aleja. Para ello se usa la relación 'distance = width_visible / (2 * tan(FOV / 2))' manteniendo constante K = distance * tan(FOV/2). Al llegar a cierta distancia, la cámara hace una pausa para después moverse en la dirección contraria.
"""
@click.command()
@click.option("--width", default=960, type=int)
@click.option("--height", default=960, type=int)
def tarea(width: int, height: int):
    window = pyglet.window.Window(width, height, "Personaje con grafo de esecena y efecto Dolly Zoom")

    # Inicialización del Grafo
    graph = Scenegraph("root")

    # Cargar Shaders
    # Se asume que los shaders están en el mismo directorio que este script
    graph.load_and_register_pipeline(
        "basic_shader",
        str(Path(os.path.dirname(__file__)) / "vertex_simple.glsl"),
        str(Path(os.path.dirname(__file__)) / "fragment_simple.glsl"),
    )
    graph.register_pipeline("current_shader", graph.pipelines["basic_shader"])

    # Cargar Malla (Mesh)
    # Registro de la malla geométrica de un cubo genérico
    graph.load_and_register_mesh(
        "cube",
        "assets/cube.off",
    )


    # PERSONAJE CON GRAFO DE ESCENA
    # El personaje se sitúa en el origen (0,0,0) para que el efecto Dolly Zoom funcione correctamente
    # manteniendo su tamaño aparente.

    # Colores del personaje
    COLORS = {
        "torso":     np.array([200/255,  50/255,  50/255, 1]),   # rojo
        "head":      np.array([255/255, 220/255,  50/255, 1]),   # amarillo
        "left_arm":  np.array([ 50/255, 200/255,  50/255, 1]), # verde
        "right_arm": np.array([ 50/255,  50/255, 200/255, 1]), # azul
        "left_leg":  np.array([200/255, 200/255,  50/255, 1]), # oliva
        "right_leg": np.array([200/255,  50/255, 200/255, 1]), # magenta
    }

    # Torso
    torso_tr = tr.scale(1.0, 1.5, 0.5)
    graph.add_mesh_instance(
        "torso",
        "cube",
        "basic_shader",
        transform=tr.uniformScale(0.5),
        color=COLORS["torso"],
    )
    graph.add_edge("root", "torso")

    # Cabeza (hijo del torso o raíz, posicionado arriba)
    head_tr = tr.matmul([
        tr.translate(0, 1.3, 0),
        tr.scale(0.5, 0.5, 0.5)
    ])
    graph.add_mesh_instance(
        "head",
        "cube",
        "basic_shader",
        transform=tr.translate(0, 0.5, 0) @ tr.uniformScale(0.6),
        color=COLORS["head"],
    )
    graph.add_edge("torso", "head")

    # Brazos
    arm_scale = tr.scale(0.25, 0.9, 0.25)

    left_arm_tr = tr.matmul([tr.translate(-0.7, 0.2, 0), arm_scale])
    graph.add_mesh_instance(
        "left_arm",
        "cube",
        "basic_shader",
        transform=tr.translate(-0.45, 0.3, 0) @ tr.uniformScale(0.4),
        color=COLORS["left_arm"]
    )
    graph.add_edge("torso", "left_arm")

    right_arm_tr = tr.matmul([tr.translate(0.7, 0.2, 0), arm_scale])
    graph.add_mesh_instance(
        "right_arm",
        "cube",
        "basic_shader",
        transform=tr.translate(0.45, 0.3, 0) @ tr.uniformScale(0.4),
        color=COLORS["right_arm"],
    )
    graph.add_edge("torso", "right_arm")

    # Piernas
    leg_scale = tr.scale(0.3, 1.1, 0.3)

    left_leg_tr = tr.matmul([tr.translate(-0.3, -1.3, 0), leg_scale])
    graph.add_mesh_instance(
        "left_leg",
        "cube",
        "basic_shader",
        transform=tr.translate(-0.2, -0.75, 0) @ tr.uniformScale(0.5),
        color=COLORS["left_leg"],
    )
    graph.add_edge("torso", "left_leg")

    right_leg_tr = tr.matmul([tr.translate(0.3, -1.3, 0), leg_scale])
    graph.add_mesh_instance(
        "right_leg",
        "cube",
        "basic_shader",
        transform=tr.translate(0.2, -0.75, 0) @ tr.uniformScale(0.5),
        color=COLORS["right_leg"],
    )
    graph.add_edge("torso", "right_leg")

    # GENERACIÓN DEL FONDO
    # Generamos cubos aleatorios detrás del personaje para evidenciar el cambio de FOV.
    # El personaje está en Z=0 por lo que el fondo debe estar en Z negativo

    num_cubes = 60
    for i in range(num_cubes):
        name = f"bg_cube_{i}"

        # Para cada cubo se elige una posición aleatoria
        # pero siempre en Z = -20
        z = -20
        x = random.uniform(-20, 20)
        y = random.uniform(-20, 20)

        # Escala aleatoria
        s = random.uniform(0.5, 2.5)

        # Color aleatorio
        r = random.uniform(0.2, 0.9)
        g = random.uniform(0.2, 0.9)
        b = random.uniform(0.2, 0.9)
        color = np.array([r, g, b, 1.0])

        transform = tr.matmul([
            tr.translate(x, y, z),
            tr.scale(s, s, s)
        ])

        # Añadir cubos aleatorios de fondo al grafo de escena
        graph.add_mesh_instance(
            name,
            "cube",
            "basic_shader",
            transform=transform,
            color=color,# Color aleatorio
        )
        graph.add_edge("root", name)


    # EFECTO DOLLY ZOOM

    # Parámetros definidos
    MIN_DIST = 2.5
    MAX_DIST = 12.0
    WAIT_TIME = 1.5  # Segundos de espera antes de cambiar de dirección
    MOVE_SPEED = 3.0 # Velocidad en unidades por segundo

    # Estado inicial de la simulación
    sim_state = {
        "distance": MIN_DIST,      # Distancia actual de la cámara
        "direction": 1,            # 1: Alejándose, -1: Acercándose
        "waiting": False,          # Si está en tiempo de espera
        "timer": 0.0               # Temporizador para la espera
    }

    # Cálculo de la constante mágica para Dolly Zoom.
    # Fórmula: width_visible = 2 * distancia * tan(fov / 2)
    # Queremos que width_visible sea constante en la posición del personaje (d=0 -> distancia cámara).
    # Establecemos un FOV de referencia para la distancia mínima.
    REF_FOV_DEGREES = 90.0
    ref_fov_radians = radians(REF_FOV_DEGREES)

    # K = distancia * tan(fov/2)
    # Esta K debe mantenerse constante durante la animación.
    ZOOM_CONSTANT_K = MIN_DIST * tan(ref_fov_radians / 2)


    def update(dt):
        """
        Función de actualización llamada por pyglet.clock.schedule
        Maneja la lógica de movimiento y el cálculo de matrices.
        """
        nonlocal sim_state

        # Determina si debe esperar o si se debe mover la cámara
        if sim_state["waiting"]:
            sim_state["timer"] -= dt
            if sim_state["timer"] <= 0:
                sim_state["waiting"] = False
                sim_state["direction"] *= -1 # Invertir dirección cuando se llega al final del recorrido
        else:
            # Mover la cámara
            delta = MOVE_SPEED * dt * sim_state["direction"]
            sim_state["distance"] += delta

            # Verificar límites
            hit_limit = False
            if sim_state["distance"] >= MAX_DIST:
                sim_state["distance"] = MAX_DIST
                hit_limit = True
            elif sim_state["distance"] <= MIN_DIST:
                sim_state["distance"] = MIN_DIST
                hit_limit = True

            if hit_limit:
                sim_state["waiting"] = True
                sim_state["timer"] = WAIT_TIME

        # Actualizar el FOV acorde a la nueva distancia para mantener el tamaño percibido del personaje.
        # tan(fov / 2) = K / distancia
        # fov = 2 * atan(K / distancia)
        new_fov_radians = 2 * atan(ZOOM_CONSTANT_K / sim_state["distance"])
        new_fov_degrees = degrees(new_fov_radians)

        # Actualizar matrices de cámara, apuntar siempre al origen
        # donde está el personaje
        eye = np.array([0, 0, sim_state["distance"]], dtype=np.float32)
        at = np.array([0, 0, 0], dtype=np.float32)
        up = np.array([0, 1, 0], dtype=np.float32)

        view_transform = tr.lookAt(eye, at, up)

        # Proyección perspectiva con el nuevo FOV dinámico
        projection_transform = tr.perspective(new_fov_degrees, width/height, 0.1, 100.0)

        # Actualizar atributos globales del grafo
        graph.set_global_attributes(
            projection=projection_transform,
            view=view_transform
        )

    # Programar la función de actualización a 60 FPS
    pyglet.clock.schedule_interval(update, 1/60.0)

    @window.event
    def on_draw():
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        window.clear()
        GL.glEnable(GL.GL_DEPTH_TEST)

        # Dibujar el grafo de escena
        graph.render()

    pyglet.app.run()
