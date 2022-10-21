#version 330 core
layout(location = 0) in vec3 _vertex;
layout(location = 3) in vec4 _colour;
layout(location = 8) in vec2 _uv;
layout(location = 2) in vec3 _normal;

out float HEIGHT;
out vec2 UV;
out vec4 COLOUR;
out vec3 NORMAL;

uniform mat4 mvp;
uniform float intime;
uniform vec3 eye;

void main()
{
    vec4 pos = vec4(_vertex.xyz, 1.);

    float height;
    float l = length(_vertex.xyz - eye);
    if (l < 36.){
        height = mix(0.1 * (sin((_vertex.x + intime)) + 0.5 * cos((_vertex.z + intime))), 0, l / 36);
    } else {
        height = 0.;
    }
    
    pos.y = pos.y + height;
    gl_Position = mvp * pos;
    UV = _uv;
    COLOUR = _colour;
    NORMAL = _normal;
    HEIGHT = height;
}