#version 330 core

in vec2 UV;
in vec4 COLOUR;

out vec4 colour_frag;

void main()
{
    colour_frag = COLOUR;
}
