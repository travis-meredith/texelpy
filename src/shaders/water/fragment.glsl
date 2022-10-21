#version 330 core

in vec2 UV;
in vec4 COLOUR;
in float HEIGHT;

out vec4 colour_frag;

uniform sampler2D texture_sampler;

const float near = 0.1;
const float far = 600.;

float linearise_depth(float depth) {
    float z = depth * 2.0 - 1.0;
    return (2.0 * near * far) / (far + near - z * (far - near));
}

void main()
{

    vec2 uvalt = vec2(UV.x, UV.y + 0.0625);
    
    vec4 colour_white = vec4(0.7, 0.7, 0.9, 1);

    float dt = 7 * HEIGHT;

    vec4 texture_raw = vec4(texture(texture_sampler, UV).rgba);
    vec4 texture_araw = vec4(texture(texture_sampler, uvalt).rgba);

    colour_frag = mix(texture_raw, texture_araw, dt);
}
