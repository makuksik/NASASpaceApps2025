class SimulationEngine:
    def __init__(self, bodies):
        self.bodies = bodies  # list of Asteroid or Planet objects

    def step(self, dt):
        for body in self.bodies:
            if hasattr(body, 'update_position'):
                body.update_position(dt)
