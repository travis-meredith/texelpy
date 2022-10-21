#version 330 core
layout(location = 0) in vec3 _vertex;
layout(location = 3) in vec4 _colour;
layout(location = 8) in vec2 _uv;
layout(location = 2) in vec3 _normal;

out vec2 UV;
out vec4 COLOUR;
out vec3 NORMAL;

uniform mat4 mvp;
uniform mat4 m;
uniform mat4 v;
uniform mat4 p;
//uniform vec3 lightdirection;

void main()
{
    vec4 pos = vec4(_vertex.xyz, 1.0);
    gl_Position = mvp * pos;
    UV = _uv;
    COLOUR = _colour;
    NORMAL = _normal;
}