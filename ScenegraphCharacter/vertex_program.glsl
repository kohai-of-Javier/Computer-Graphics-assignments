#version 330

in vec3 position;
in vec3 normal;

uniform vec3 color;
uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

uniform vec3 light_pos;
uniform vec3 light_transform;

out vec4 fragColor;

// función para calcular el componente difuso
vec3 calc_diffuse(vec3 normal_world, vec3 light_dir,
                  vec3 light_color, vec3 material_diffuse) {
    float diff = max(dot(normal_world, light_dir), 0.0);
    return light_color * (diff * material_diffuse);
}

// función para calcular el componente especular
vec3 calc_specular(vec3 normal_world, vec3 light_dir, vec3 view_dir,
                   vec3 light_color, vec3 material_specular,
                   float shininess) {
    vec3 reflect_dir = reflect(-light_dir, normal_world);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    return light_color * (spec * material_specular);
}

void main()
{
    // Propiedades del material (conejo brillante con tono rosado)
    vec3 material_ambient = color;
    vec3 material_diffuse = vec3(0.9, 0.1, 0.8);
    vec3 material_specular = vec3(1.0, 0.8, 1.0);
    float material_shininess = 32.0;

    // Componente ambiental
    vec3 ambient = vec3(0.2) * material_ambient;

    // Normal en espacio de mundo
    mat3 normal_matrix = transpose(inverse(mat3(transform)));
    vec3 normal_world = normalize(normal_matrix * normal);

    // Luz blanca por defecto
    vec3 light_color = vec3(1.0, 1.0, 1.0);

    // TODO:falta view_dir (view_dir para componente especular)
    fragColor = vec4(ambient + calc_diffuse(normal_world, light_pos, light_color, material_diffuse) + calc_specular(normal_world, light_pos, light_transform, light_color, material_specular, material_shininess), 1.0);

    //fragColor = vec4(color, 1.0);
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}
