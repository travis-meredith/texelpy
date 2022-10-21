#version 330 core

in vec2 UV;
in vec4 COLOUR;
in vec3 NORMAL;
in vec3 NORMAL_CS;
//in vec3 LIGHTDIRECTION_CS;

out vec4 colour_frag;

uniform sampler2D texture_sampler;
uniform vec3 lightdirection;

void main()
{

    vec3 n = normalize(NORMAL);
    vec3 l = normalize(lightdirection);

    float cos_theta = clamp(dot(n, l), 0.8, 1);
    vec4 colour = vec4(COLOUR.xyz * cos_theta, 1);
    colour_frag = colour * vec4(texture(texture_sampler, UV).rgba);
}
