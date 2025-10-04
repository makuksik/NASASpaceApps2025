from vpython import sphere, vector, color


class Asteroid:
    def __init__(self, name, mass, radius, position, velocity, color_=color.red):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.position = vector(*position)
        self.velocity = vector(*velocity)
        self.body = sphere(pos=self.position, radius=self.radius, color=color_)

    def move(self):
        self.position += self.velocity
        self.body.pos = self.position

    def __str__(self):
        pos = (round(self.position.x, 2), round(self.position.y, 2), round(self.position.z, 2))
        vel = (round(self.velocity.x, 2), round(self.velocity.y, 2), round(self.velocity.z, 2))
        return f"Asteroid {self.name}: mass={self.mass}, radius={self.radius}, position={pos}, velocity={vel}"
