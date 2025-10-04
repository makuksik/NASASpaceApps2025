class Trajectory:
    def __init__(self, body, path=None):
        self.body = body  # Asteroid or Planet
        self.path = path if path else []

    def record_position(self):
        self.path.append(tuple(self.body.position))