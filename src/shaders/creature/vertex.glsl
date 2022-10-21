#version 330 core
layout(location = 0) in vec3 _vertex;
layout(location = 3) in vec4 _colour;
layout(location = 8) in vec2 _uv;

out vec4 COLOUR;
out vec2 UV;

uniform mat4 mvp;

void main()
{
    gl_Position = mvp * vec4(_vertex.xyz, 1.);
    UV = _uv;
    COLOUR = _colour;
}