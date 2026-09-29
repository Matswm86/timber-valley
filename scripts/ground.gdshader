shader_type spatial;
render_mode diffuse_burley;

// Meadow ground: two-tone grass with noise, dirt paths and plazas, wet shore by the river.

uniform sampler2D noise_tex : repeat_enable, filter_linear_mipmap;
uniform sampler2D detail_tex : repeat_enable, filter_linear_mipmap;
uniform vec3 grass_a : source_color = vec3(0.42, 0.66, 0.27);
uniform vec3 grass_b : source_color = vec3(0.56, 0.74, 0.32);
uniform vec3 dirt : source_color = vec3(0.76, 0.62, 0.43);
uniform vec3 dirt_dark : source_color = vec3(0.63, 0.5, 0.34);
uniform vec3 shore : source_color = vec3(0.55, 0.52, 0.36);
// Path segments: xy = start (world xz), zw = end.
uniform vec4 paths[32];
uniform float path_widths[32];
uniform int path_count = 0;
// Plazas: xy = centre, z = half width, w = half depth (rounded rectangles).
uniform vec4 plazas[24];
uniform int plaza_count = 0;
uniform float river_x = -26.0;
uniform float river_half = 4.0;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float seg_dist(vec2 p, vec2 a, vec2 b) {
	vec2 pa = p - a, ba = b - a;
	float h = clamp(dot(pa, ba) / max(dot(ba, ba), 0.0001), 0.0, 1.0);
	return length(pa - ba * h);
}

float round_box(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + r;
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec2 p = world_pos.xz;
	float n = texture(noise_tex, p * 0.018).r;
	float n2 = texture(detail_tex, p * 0.21).r;
	vec3 grass = mix(grass_a, grass_b, smoothstep(0.35, 0.7, n));
	grass *= 0.92 + 0.16 * n2;

	float d = 1e5;
	for (int i = 0; i < path_count; i++) {
		d = min(d, seg_dist(p, paths[i].xy, paths[i].zw) - path_widths[i]);
	}
	for (int i = 0; i < plaza_count; i++) {
		d = min(d, round_box(p - plazas[i].xy, plazas[i].zw, 1.2));
	}
	float wobble = (n2 - 0.5) * 0.5;
	float dirt_mask = smoothstep(0.25, -0.15, d + wobble);
	vec3 dirt_col = mix(dirt_dark, dirt, smoothstep(0.2, 0.8, n2));
	vec3 col = mix(grass, dirt_col, dirt_mask);
	// Soft darker rim where grass meets the path.
	col *= 1.0 - 0.12 * smoothstep(0.6, 0.0, abs(d + wobble)) * (1.0 - dirt_mask);

	float rd = abs(p.x - river_x) - river_half;
	col = mix(col, shore, smoothstep(1.6, 0.2, rd + wobble));

	// Slow drifting cloud shadows.
	float cloud = texture(noise_tex, p * 0.012 + vec2(TIME * 0.006, TIME * 0.003)).r;
	col *= mix(1.0, 0.82, smoothstep(0.55, 0.75, cloud));
	ALBEDO = col;
	ROUGHNESS = 0.95;
	SPECULAR = 0.2;
}
