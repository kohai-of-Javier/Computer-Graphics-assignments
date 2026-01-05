#version 330 core

layout(location=0) in vec3 position;

uniform mat4 transform, view, projection;
uniform vec4 color;

out vec4 fragColor;

void main() {
    fragColor = color;
    gl_Position = projection * view * transform * vec4(position,1.0);
}
