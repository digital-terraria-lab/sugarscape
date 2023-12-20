import math
import random

class Disease:
    def __init__(self, diseaseID, configuration):
        self.ID = diseaseID
        self.sugarMetabolismPenalty = configuration["sugarMetabolismPenalty"]
        self.spiceMetabolismPenalty = configuration["spiceMetabolismPenalty"]
        self.visionPenalty = configuration["visionPenalty"]
        self.movementPenalty = configuration["movementPenalty"]
        self.fertilityPenalty = configuration["fertilityPenalty"]
        self.aggressionPenalty = configuration["aggressionPenalty"]
        self.tags = configuration["tags"]
        self.configuration = configuration
        self.agent = None

    def __str__(self):
        return "{0}".format(self.ID)
