import pyglet
import pyglet.gl as GL
import numpy as np
from pathlib import Path
import click
import os

from grafica.scenegraph import Scenegraph
import grafica.transformations as tr

@click.command()
@click.option("--width", default=960, type=int)
@click.option("--height", default=960, type=int)
def tarea(width: int, height: int):
    window = pyglet.window.Window(width, height, "Personaje con grafo de escena")

    # Grafo y shaders
    graph = Scenegraph("root")
    graph.load_and_register_pipeline(
        "basic_shader",
        Path(os.path.dirname(__file__)) / "vertex_simple.glsl",
        Path(os.path.dirname(__file__)) / "fragment_simple.glsl",
    )
    graph.register_pipeline("current_shader", graph.pipelines["basic_shader"])

    # Registro de la malla geométrica de un cubo genérico
    graph.load_and_register_mesh(
        "cube",
        "assets/cube.off",
    )

    # Nodos del personaje (solo torso y cabeza para probar)
    COLORS = {
        "torso":     np.array([200/255,  50/255,  50/255, 1]),   # rojo
        "head":      np.array([255/255, 220/255,  50/255, 1]),   # amarillo
        "left_arm":  np.array([ 50/255, 200/255,  50/255, 1]), # verde
        "right_arm": np.array([ 50/255,  50/255, 200/255, 1]), # azul
        "left_leg":  np.array([200/255, 200/255,  50/255, 1]), # oliva
        "right_leg": np.array([200/255,  50/255, 200/255, 1]), # magenta
    }

    # Nodo torso (raíz del personaje)
    graph.add_mesh_instance("torso", "cube", "basic_shader",
                           transform=tr.uniformScale(0.5),
                           color=COLORS["torso"])
    graph.add_edge("root", "torso")

    # Cabeza (ligeramente más pequeña y encima del torso)
    graph.add_mesh_instance(
        "head",
        "cube",
        "basic_shader",
        transform=tr.translate(0, 0.5, 0) @ tr.uniformScale(0.6),
        color=COLORS["head"],
    )
    graph.add_edge("torso", "head")

    # Brazo izquierdo
    graph.add_mesh_instance(
        "left_arm",
        "cube",
        "basic_shader",
        # El origen del brazo está en el hombro (punto de unión)
        transform=tr.translate(-0.45, 0.3, 0) @ tr.uniformScale(0.4),
        color=COLORS["left_arm"],
    )
    graph.add_edge("torso", "left_arm")

    # Brazo derecho
    graph.add_mesh_instance(
        "right_arm",
        "cube",
        "basic_shader",
        transform=tr.translate(0.45, 0.3, 0) @ tr.uniformScale(0.4),
        color=COLORS["right_arm"],
    )
    graph.add_edge("torso", "right_arm")

    # Pierna izquierda
    graph.add_mesh_instance(
        "left_leg",
        "cube",
        "basic_shader",
        transform=tr.translate(-0.2, -0.75, 0) @ tr.uniformScale(0.5),
        color=COLORS["left_leg"],
    )
    graph.add_edge("torso", "left_leg")

    # Pierna derecha
    graph.add_mesh_instance(
        "right_leg",
        "cube",
        "basic_shader",
        transform=tr.translate(0.2, -0.75, 0) @ tr.uniformScale(0.5),
        color=COLORS["right_leg"],
    )
    graph.add_edge("torso", "right_leg")

    # Cámara y luz
    near, far = 0.1, 10.0

    # Cámara base (usada como referencia)
    cam_base = tr.perspective(45.0, width / height, near, far)

    # Tres vistas dramáticas (una por pose)
    CAMERA_POSES = [
        # Pose 0 – Vista frontal
        {
            "view": tr.lookAt(np.array([0.0, 1.0, 3.0]),
                              np.array([0.0, 0.5, 0.0]),
                              np.array([0.0, 1.0, 0.0])),
            "proj": cam_base,
        },
        # Pose 1 – Vista angular desde abajo (ángulo bajo)
        {
            "view": tr.lookAt(np.array([2.0, -0.5, 2.0]),
                              np.array([0.0, 0.3, 0.0]),
                              np.array([0.0, 1.0, 0.0])),
            "proj": tr.perspective(60.0, width / height, near, far),
        },
        # Pose 2 – Vista lateral con cámara alta (tipo “bird‑eye”)
        {
            "view": tr.lookAt(np.array([-2.5, 2.5, -0.5]),
                              np.array([0.0, 0.5, 0.0]),
                              np.array([0.0, 1.0, 0.0])),
            "proj": tr.perspective(45.0, width / height, near, far),
        },
    ]

    # Luz (posición fija)
    light_pos = np.array([2.0, 4.0, 2.0])
    light_proj = tr.perspective(90.0, 1.0, near, far)
    light_view = tr.lookAt(light_pos,
                           np.array([0.0, 0.0, 0.0]),
                           np.array([0.0, 1.0, 0.0]))
    light_transform = light_proj @ light_view


    # Registrar vistas en el grafo (necesarias para los shaders)
    graph.register_view_transform(light_view, name="light_view")
    graph.register_view_transform(tr.identity(), name="camera_view")  # placeholder

    # Definir cada pose
    POSES = [
        # Pose 0 – postura neutra (todos los ángulos a 0)
        {
            "torso": tr.identity(),
            "head": tr.identity(),
            "left_arm": tr.identity(),
            "right_arm": tr.identity(),
            "left_leg": tr.identity(),
            "right_leg": tr.identity(),
        },
        # Pose 1 – brazo derecho levantado, pierna izquierda adelantada
        {
            "torso": tr.identity(),
            "head": tr.identity(),#tr.rotationY(np.radians(15)),
            "left_arm": tr.identity(),#tr.rotationZ(np.radians(-30)),
            "right_arm": tr.rotationZ(np.radians(30)),
            "left_leg": tr.rotationX(np.radians(-20)),
            "right_leg": tr.identity(),
        },
        # Pose 2 – torso girado, cabeza mirando al frente en vista desde arriba y atrás
        {
            "torso": tr.rotationY(np.radians(45)),
            "head": tr.rotationY(np.radians(-30)),
            "left_arm": tr.identity(),
            "right_arm": tr.identity(),
            "left_leg": tr.identity(),
            "right_leg": tr.identity(),
        },
    ]

    # Estado actual
    current_pose = 0

    def apply_pose(pose_idx: int):
        """Aplica la pose indicada y actualiza la cámara."""
        nonlocal current_pose
        current_pose = pose_idx % len(POSES)

        # Actualizar transformaciones de los nodos
        for node, mat in POSES[current_pose].items():
            graph.nodes[node]["transform"] = mat

        # Recalcular transformaciones globales del grafo
        graph.calculate_global_transforms()

        # Cambiar cámara
        cam_cfg = CAMERA_POSES[current_pose]
        graph.register_view_transform(cam_cfg["view"], name="camera_view")
        graph.set_global_attributes(
            projection=cam_cfg["proj"],
            view=cam_cfg["view"],
            light_position=light_pos,
            light_transform=light_transform,
        )

    # Aplicar pose inicial
    apply_pose(0)

    # Al apretar una tecla, con espacio se cambia de pose
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            # Cambiar a la siguiente pose
            apply_pose(current_pose+1)

    # Evento de dibujo
    @window.event
    def on_draw():
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glLineWidth(2.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        graph.render()

    pyglet.app.run()
