# Class of client objectes

class ClientObject:
  # Construstor
  def __init__(self, name, address):
    # Client object attributes
    self.address = address
    self.name = name
    self.score = 0
    self.hasAnswered = False
    self.isCorrect = False
    self.roundsWon = 0
    self.isActive = False