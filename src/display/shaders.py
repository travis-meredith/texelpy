

from pyshaders import ShaderProgram, from_files_names  # type: ignore


def load_shader(name: str) -> ShaderProgram:
    "get shaders from shaders/<name>/<shader>"
    return from_files_names(f"shaders/{name}/vertex.glsl", f"shaders/{name}/fragment.glsl")



