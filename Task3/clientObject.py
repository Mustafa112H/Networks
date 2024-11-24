# Class of client objectes

class ClientObject:
  # Construstor
  def __init__(self, name, address):
    # Client object attributes
    self.address = address
    self.name = name
    self.score = 0
    self.answered = False
    self.correct = False