import math

class Cell:
    def __init__(self, x, y, environment, maxSugar=0, maxSpice=0, growbackRate=0):
        self.x = x
        self.y = y
        self.environment = environment
        self.maxSugar = maxSugar
        self.sugar = maxSugar
        self.maxSpice = maxSpice
        self.spice = maxSpice
        self.pollution = 0
        self.agent = None
        self.hemisphere = "north" if self.x >= self.environment.equator else "south"
        self.season = None
        self.timestep = 0
        self.neighbors = []
        self.sugarLastProduced = 0
        self.spiceLastProduced = 0

    def doSpiceConsumptionPollution(self, spiceConsumed):
        consumptionPollutionFactor = self.environment.spiceConsumptionPollutionFactor
        self.pollution += consumptionPollutionFactor * spiceConsumed

    def doSugarConsumptionPollution(self, sugarConsumed):
        consumptionPollutionFactor = self.environment.sugarConsumptionPollutionFactor
        self.pollution += consumptionPollutionFactor * sugarConsumed

    def doPollutionDiffusion(self):
        meanPollution = self.pollution
        for neighbor in self.neighbors:
            meanPollution += neighbor.pollution
        meanPollution = meanPollution / (len(self.neighbors) + 1)
        for neighbor in self.neighbors:
            neighbor.pollution = meanPollution
        self.pollution = meanPollution

    def doSpiceProductionPollution(self, spiceProduced):
        productionPollutionFactor = self.environment.spiceProductionPollutionFactor
        self.pollution += productionPollutionFactor * spiceProduced

    def doSugarProductionPollution(self, sugarProduced):
        productionPollutionFactor = self.environment.sugarProductionPollutionFactor
        self.pollution += productionPollutionFactor * sugarProduced

    def findNeighborAgents(self):
        agents = []
        for neighbor in self.neighbors:
            agent = neighbor.agent
            if agent != None:
                agents.append(agent)
        return agents

    def findNeighbors(self, mode):
        self.neighbors = []
        north = self.findNorthNeighbor()
        south = self.findSouthNeighbor()
        self.neighbors.append(north)
        self.neighbors.append(south)
        self.neighbors.append(self.findEastNeighbor())
        self.neighbors.append(self.findWestNeighbor())
        if mode == "moore":
            self.neighbors.append(north.findEastNeighbor())
            self.neighbors.append(north.findWestNeighbor())
            self.neighbors.append(south.findEastNeighbor())
            self.neighbors.append(south.findWestNeighbor())

    def findNeighborWealth(self):
        neighborWealth = 0
        for neighbor in self.neighbors:
            neighborWealth += neighbor.sugar + neighbor.spice
        return neighborWealth

    def findEastNeighbor(self):
        eastNeighbor = self.environment.findCell((self.x + 1 + self.environment.width) % self.environment.width, self.y)
        return eastNeighbor

    def findNorthNeighbor(self):
        northNeighbor = self.environment.findCell(self.x, (self.y - 1 + self.environment.height) % self.environment.height)
        return northNeighbor

    def findSouthNeighbor(self):
        southNeighbor = self.environment.findCell(self.x, (self.y + 1 + self.environment.height) % self.environment.height)
        return southNeighbor

    def findWestNeighbor(self):
        westNeighbor = self.environment.findCell((self.x - 1 + self.environment.width) % self.environment.width, self.y)
        return westNeighbor

    def isOccupied(self):
        return self.agent != None

    def resetAgent(self):
        self.agent = None

    def resetSpice(self):
        self.spice = 0

    def resetSugar(self):
        self.sugar = 0

    def updateSeason(self):
        if self.season == "wet":
            self.season = "dry"
        else:
            self.season = "wet"

    def __str__(self):
        string = ""
        if self.agent != None:
            string = "-A-"
        else:
            string = "{0}/{1}".format(str(self.sugar), str(self.spice))
        return string
