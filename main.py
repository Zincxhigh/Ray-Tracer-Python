import math
from PIL import Image

class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x , self.y, self.z = float(x), float(y), float(z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self,other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def normalize(self):
        length = math.sqrt(self.dot(self))
        return Vec3(self.x / length, self.y /length, self.z / length)
    def reflect(self, normal):
        return self - normal * (2.0 * self.dot(normal))

class Ray:

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()

width, height = 400, 400
camera_origin = Vec3(0, 0, 0)
light_position = Vec3(5, 5, 2).normalize()

image = Image.new("RGB", (width, height))
pixels = image.load()

aspect_ratio = width / height

class Materiel:
    def __init__(self, color, reflectivity=0.0):
        self.color = color
        self.reflectivity = reflectivity

class Sphere:

    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminiant = b * b -4 * a * c

        if discriminiant < 0:
            return None

        t = (-b - math.sqrt(discriminiant)) / (2.0 * a)
        return t if t > 0 else None

def trace_ray(ray, scene, light_dir, depth=0, max_depth=3):
  if depth >= max_depth:
    return (0, 0, 0)

  nearest_t = float('inf')
  hit_object = None

  for obj in scene:
    t = obj.intersect(ray)
    if t is not None and t < nearest_t:
      nearest_t = t
      hit_object = obj

  if hit_object is None:
    return (20, 20, 40)  

  hit_point = ray.origin + (ray.direction * nearest_t)
  normal = (hit_point - hit_object.center).normalize()

  brightness = max(0.0, normal.dot(light_dir))
  mat = hit_object.material

  base_r = mat.color[0] * brightness * 255
  base_g = mat.color[1] * brightness * 255
  base_b = mat.color[2] * brightness * 255

  if mat.reflectivity > 0:
    reflected_dir = ray.direction.reflect(normal)
    shadow_origin = hit_point + (normal * 1e-4)
    reflected_ray = Ray(shadow_origin, reflected_dir)

    refl_r, refl_g, refl_b = trace_ray(
        reflected_ray, scene, light_dir, depth + 1, max_depth
    )

    r = int(base_r * (1 - mat.reflectivity) + refl_r * mat.reflectivity)
    g = int(base_g * (1 - mat.reflectivity) + refl_g * mat.reflectivity)
    b = int(base_b * (1 - mat.reflectivity) + refl_b * mat.reflectivity)
  else:
    r, g, b = int(base_r), int(base_g), int(base_b)

  return (
      max(0, min(255, r)),
      max(0, min(255, g)),
      max(0, min(255, b)),
  )

red_matte = Materiel(color=(0.8, 0.1, 0.1), reflectivity=0.0)
mirror = Materiel(color=(1.0, 1.0, 1.0), reflectivity=0.8)
gold_shiny = Materiel(color=(1.0, 0.8, 0.2), reflectivity=0.3)

scene = [
    Sphere(center=Vec3(-1.5, 0, -5), radius=0.1, material=mirror),
    Sphere(center=Vec3(1.5, 0, -5), radius=0.1, material=red_matte),
    Sphere(center=Vec3(0, -101, -5), radius=80.0, material=gold_shiny)
]

for y in range(height):
    for x in range(width):
        px = (2 * (x + 0.5) / width - 1) * aspect_ratio
        py = 1 - 2 * (y + 0.5) / height

        ray = Ray(camera_origin, Vec3(px, py, -1))
        pixels[x, y] = trace_ray(ray, scene, light_position)


image.save("output.png")
print("image saved whatever")

