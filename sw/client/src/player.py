class PongPlayer:
    def __init__(self, name: str, left: bool):
        self.name = name
        self.left = left
        self.score = 0
        self.hits = 0