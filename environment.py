import math
import random

class Environment:
    # Assumption: grid is always indexed by [height][width]
    def __init__(self, height, width, sugarscape, configuration):
        self.width = width
        self.height = height
        self.globalMaxSugar = configuration["globalMaxSugar"]
        self.sugarRegrowRate = configuration["sugarRegrowRate"]
        self.globalMaxSpice = configuration["globalMaxSpice"]
        self.spiceRegrowRate = configuration["spiceRegrowRate"]
        self.sugarscape = sugarscape
        self.timestep = 0
        self.seed = configuration["sugarscapeSeed"]
        self.seasonInterval = configuration["seasonInterval"]
        self.seasonalGrowbackDelay = configuration["seasonalGrowbackDelay"]
        self.seasonNorth = "summer" if configuration["seasonInterval"] > 0 else None
        self.seasonSouth = "winter" if configuration["seasonInterval"] > 0 else None
        self.seasonalGrowbackCountdown = configuration["seasonalGrowbackDelay"]
        self.pollutionDiffusionDelay = configuration["pollutionDiffusionDelay"]
        self.pollutionDiffusionCountdown = configuration["pollutionDiffusionDelay"]
        self.sugarConsumptionPollutionFactor = configuration["sugarConsumptionPollutionFactor"]
        self.spiceConsumptionPollutionFactor = configuration["spiceConsumptionPollutionFactor"]
        self.sugarProductionPollutionFactor = configuration["sugarProductionPollutionFactor"]
        self.spiceProductionPollutionFactor = configuration["spiceProductionPollutionFactor"]
        self.maxCombatLoot = configuration["maxCombatLoot"]
        self.universalSpiceIncomeInterval = configuration["universalSpiceIncomeInterval"]
        self.universalSugarIncomeInterval = configuration["universalSugarIncomeInterval"]
        self.equator = math.ceil(self.height / 2)
        # Populate grid with NoneType objects
        self.grid = [[None for j in range(width)]for i in range(height)]

    def doCellUpdate(self):
        for i in range(self.height):
            for j in range(self.width):
                cellCurrSugar = self.grid[i][j].sugar
                cellCurrSpice = self.grid[i][j].spice
                cellMaxSugar = self.grid[i][j].maxSugar
                cellMaxSpice = self.grid[i][j].maxSpice
                cellSeason = self.grid[i][j].season
                sugarRegrowth = min(cellCurrSugar + self.sugarRegrowRate, cellMaxSugar)
                spiceRegrowth = min(cellCurrSpice + self.spiceRegrowRate, cellMaxSpice)
                if self.seasonInterval > 0:
                    if self.timestep % self.seasonInterval == 0:
                        self.grid[i][j].updateSeason()
                    if (cellSeason == "summer") or (cellSeason == "winter" and self.seasonalGrowbackCountdown == self.seasonalGrowbackDelay):
                        if self.grid[i][j].sugar + self.sugarRegrowRate != self.grid[i][j].sugar:
                            self.grid[i][j].sugarLastProduced = self.sugarRegrowRate
                        else:
                            self.grid[i][j].sugarLastProduced = 0
                        if self.grid[i][j].spice + self.spiceRegrowRate != self.grid[i][j].spice:
                            self.grid[i][j].spiceLastProduced = self.spiceRegrowRate
                        else:
                            self.grid[i][j].spiceLastProduced = 0
                        self.grid[i][j].sugar = sugarRegrowth
                        self.grid[i][j].spice = spiceRegrowth
                else:
                    if self.grid[i][j].sugar + self.sugarRegrowRate != self.grid[i][j].sugar:
                        self.grid[i][j].sugarLastProduced = self.sugarRegrowRate
                    else:
                        self.grid[i][j].sugarLastProduced = 0
                    if self.grid[i][j].spice + self.spiceRegrowRate != self.grid[i][j].spice:
                        self.grid[i][j].spiceLastProduced = self.spiceRegrowRate
                    else:
                        self.grid[i][j].spiceLastProduced = 0
                    self.grid[i][j].sugar = sugarRegrowth
                    self.grid[i][j].spice = spiceRegrowth
                if self.pollutionDiffusionDelay > 0 and self.pollutionDiffusionCountdown == self.pollutionDiffusionDelay:
                    self.grid[i][j].doPollutionDiffusion()

    def doTimestep(self, timestep):
        self.timestep = timestep
        self.updateSeasons()
        self.updatePollution()
        self.doCellUpdate()

    def findCell(self, x, y):
        return self.grid[x][y]

    def findCellNeighbors(self):
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i][j].findNeighbors()

    def findCellsInRange(self, startX, startY, gridRange):
        cellsInRange = []
        for i in range(1, gridRange + 1):
            deltaNorth = (startY + i + self.height) % self.height
            deltaSouth = (startY - i + self.height) % self.height
            deltaEast = (startX + i + self.width) % self.width
            deltaWest = (startX - i + self.width) % self.width
            cellsInRange.append({"cell": self.grid[startX][deltaNorth], "distance": i})
            cellsInRange.append({"cell": self.grid[startX][deltaSouth], "distance": i})
            cellsInRange.append({"cell": self.grid[deltaEast][startY], "distance": i})
            cellsInRange.append({"cell": self.grid[deltaWest][startY], "distance": i})
        return cellsInRange

    def placeCell(self, cell, x, y):
        self.grid[x][y] = cell

    def resetCell(self, x, y):
        self.grid[x][y] = None

    def updatePollution(self):
        if self.pollutionDiffusionDelay > 0:
            self.pollutionDiffusionCountdown -= 1
            # Pollution diffusion delay over
            if self.pollutionDiffusionCountdown == 0:
                self.pollutionDiffusionCountdown = self.pollutionDiffusionDelay

    def updateSeasons(self):
        if self.seasonInterval > 0:
            self.seasonalGrowbackCountdown -= 1
            # Seasonal growback delay over
            if self.seasonalGrowbackCountdown == 0:
                self.seasonalGrowbackCountdown = self.seasonalGrowbackDelay
            if self.timestep % self.seasonInterval == 0:
                if self.seasonNorth == "summer":
                    self.seasonNorth = "winter"
                    self.seasonSouth = "summer"
                else:
                    self.seasonNorth = "summer"
                    self.seasonSouth = "winter"

    def __str__(self):
        string = ""
        for i in range(0, self.height):
            for j in range(0, self.width):
                cell = self.grid[i][j]
                if cell == None:
                    cell = '_'
                else:
                    cell = str(cell)
                string = string + ' '+ cell
            string = string + '\n'
        return string
