from vpython import sphere, vector, color


class Planet:
    def __init__(self, name, radius, mass, position=(0, 0, 0), color_=color.blue):
        self.name = name
        self.radius = radius
        self.mass = mass
        self.position = vector(*position)
        self.body = sphere(pos=self.position, radius=self.radius, color=color_, opacity=0.6)

    def __str__(self):
        return f"{self.name}: radius={self.radius}, mass={self.mass}, position=({self.position.x},{self.position.y},{self.position.z})"
