import csv
import getopt
import json
import math
import matplotlib.pyplot
import matplotlib.ticker
import os
import re
import sys

def findMeans(dataset):
    print("Finding mean values across {0} timesteps".format(totalTimesteps))
    for model in dataset:
        for column in dataset[model]["metrics"]:
            for i in range(len(dataset[model]["metrics"][column])):
                if column not in dataset[model]["aggregates"]:
                    dataset[model]["aggregates"][column] = [0 for j in range(totalTimesteps + 1)]
                dataset[model]["aggregates"][column][i] = dataset[model]["metrics"][column][i] / dataset[model]["runs"]
    return dataset

def findMedians(dataset):
    print("Finding median values across {0} timesteps".format(totalTimesteps))
    for model in dataset:
        for column in dataset[model]["metrics"]:
            for i in range(len(dataset[model]["metrics"][column])):
                sortedColumn = sorted(dataset[model]["metrics"][column][i])
                columnLength = len(sortedColumn)
                midpoint = math.floor(columnLength / 2)
                median = sortedColumn[midpoint]
                quartile = math.floor(columnLength / 4)
                firstQuartile = sortedColumn[quartile]
                thirdQuartile = sortedColumn[midpoint + quartile]
                if columnLength % 2 == 0:
                    median = round((sortedColumn[midpoint - 1] + median) / 2, 2)
                    firstQuartile = round((sortedColumn[quartile - 1] + firstQuartile) / 2, 2)
                    thirdQuartile = round((sortedColumn[(midpoint + quartile) - 1] + thirdQuartile) / 2, 2)
                if column not in dataset[model]["aggregates"]:
                    dataset[model]["aggregates"][column] = [0 for j in range(totalTimesteps + 1)]
                    dataset[model]["firstQuartiles"][column] = [0 for j in range(totalTimesteps + 1)]
                    dataset[model]["thirdQuartiles"][column] = [0 for j in range(totalTimesteps + 1)]
                dataset[model]["aggregates"][column][i] = median
    return dataset

def generatePlots(config, models, totalTimesteps, dataset, statistic, experimentalGroup=None):
    titleStatistic = statistic.title()
    if "conflictHappiness" in config["plots"]:
        print(f"Generating {statistic} conflict happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_conflict_happiness.pdf", "meanConflictHappiness", f"{titleStatistic} Conflict Happiness", "center right", False, experimentalGroup)
    if "deaths" in config["plots"]:
        print(f"Generating {statistic} deaths plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_deaths.pdf", "meanDeathsPercentage", f"{titleStatistic} Deaths", "center right", True, experimentalGroup)
    if "familyHappiness" in config["plots"]:
        print(f"Generating {statistic} family happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_family_happiness.pdf", "meanFamilyHappiness", f"{titleStatistic} Family Happiness", "center right", False, experimentalGroup)
    if "giniCoefficient" in config["plots"]:
        print(f"Generating {statistic} Gini coefficient plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_gini.pdf", "giniCoefficient", f"{titleStatistic} Gini Coefficient", "center right", False, experimentalGroup)
    if "happiness" in config["plots"]:
        print(f"Generating {statistic} happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_happiness.pdf", "meanHappiness", f"{titleStatistic} Happiness", "center right", False, experimentalGroup)
    if "healthHappiness" in config["plots"]:
        print(f"Generating {statistic} health happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_health_happiness.pdf", "meanHealthHappiness", f"{titleStatistic} Health Happiness", "center right", False, experimentalGroup)
    if "lifeExpectancy" in config["plots"]:
        print(f"Generating {statistic} life expectancy plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_life_expectancy.pdf", "meanAgeAtDeath", f"{titleStatistic} Life Expectancy", "lower right", False, experimentalGroup)
    if "population" in config["plots"]:
        print(f"Generating {statistic} population plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_population.pdf", "population", f"{titleStatistic} Population", "lower right", False, experimentalGroup)
    if "selfishness" in config["plots"]:
        print(f"Generating {statistic} selfishness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_selfishness.pdf", "meanSelfishness", f"{titleStatistic} Selfishness Factor", "lower center", False, experimentalGroup)
    if "sickness" in config["plots"]:
        print(f"Generating {statistic} sick percentage plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_sickness.pdf", "sickAgentsPercentage", f"{titleStatistic} Diseased Agents", "center right", True, experimentalGroup)
    if "socialHappiness" in config["plots"]:
        print(f"Generating {statistic} social happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_social_happiness.pdf", "meanSocialHappiness", f"{titleStatistic} Social Happiness", "center right", False, experimentalGroup)
    if "totalWealth" in config["plots"]:
        print(f"Generating {statistic} total wealth plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_wealth.pdf", "agentWealthTotal", f"{titleStatistic} Total Wealth", "center right", False, experimentalGroup)
    if "tradeVolume" in config["plots"]:
        print(f"Generating {statistic} trade volume plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_trades.pdf", "tradeVolume", f"{titleStatistic} Trade Volume", "center right", False, experimentalGroup)
    if "ttl" in config["plots"]:
        print(f"Generating {statistic} time to live plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_ttl.pdf", "agentMeanTimeToLive", f"{titleStatistic} Time to Live", "upper right", False, experimentalGroup)
    if "wealth" in config["plots"]:
        print(f"Generating {statistic} wealth plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_wealth.pdf", "meanWealth", f"{titleStatistic} Wealth", "center right", False, experimentalGroup)
    if "wealthHappiness" in config["plots"]:
        print(f"Generating {statistic} wealth happiness plot")
        generateSimpleLinePlot(models, dataset, totalTimesteps, f"{statistic}_total_wealth_happiness.pdf", "meanWealthHappiness", f"{titleStatistic} Wealth Happiness", "center right", False, experimentalGroup)

def generateSimpleLinePlot(models, dataset, totalTimesteps, outfile, column, label, positioning, percentage=False, experimentalGroup=None):
    matplotlib.pyplot.rcParams["font.family"] = "serif"
    matplotlib.pyplot.rcParams["font.size"] = 18
    figure, axes = matplotlib.pyplot.subplots()
    axes.set(xlabel = "Timestep", ylabel = label, xlim = [0, totalTimesteps])
    x = [i for i in range(totalTimesteps + 1)]
    lines = []
    modelStrings = {"bentham": "Utilitarian", "egoist": "Egoist", "altruist": "Altruist", "none": "Raw Sugarscape", "rawSugarscape": "Raw Sugarscape", "multiple": "Multiple", "unknown": "Unknown"}
    colors = {"bentham": "magenta", "egoist": "cyan", "altruist": "gold", "none": "black", "rawSugarscape": "black ", "multiple": "red", "unknown": "green"}
    for model in dataset:
        modelString = model
        if '_' in model:
            modelString = "multiple"
        elif model not in modelStrings:
            modelString = "unknown"
        if experimentalGroup != None:
            controlGroupColumn = "control" + column[0].upper() + column[1:]
            controlGroupLabel = f"Control {modelStrings[modelString]}"
            y = [dataset[model]["aggregates"][controlGroupColumn][i] for i in range(totalTimesteps + 1)]
            axes.plot(x, y, color=colors[modelString], label=controlGroupLabel)
            experimentalGroupColumn = experimentalGroup + column[0].upper() + column[1:]
            experimentalGroupLabel = experimentalGroup[0].upper() + experimentalGroup[1:] + f" {modelStrings[modelString]}"
            y = [dataset[model]["aggregates"][experimentalGroupColumn][i] for i in range(totalTimesteps + 1)]
            axes.plot(x, y, color=colors[modelString], label=experimentalGroupLabel, linestyle="dotted")
        else:
            y = [dataset[model]["aggregates"][column][i] for i in range(totalTimesteps + 1)]
            axes.plot(x, y, color=colors[modelString], label=modelStrings[modelString])
        axes.legend(loc=positioning, labelspacing=0.1, frameon=False, fontsize=16)
    if percentage == True:
        axes.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
    figure.savefig(outfile, format="pdf", bbox_inches="tight")

def parseDataset(path, dataset, totalTimesteps, statistic, skipExtinct=False):
    encodedDir = os.fsencode(path)
    for file in os.listdir(encodedDir):
        filename = os.fsdecode(file)
        if not (filename.endswith(".json") or filename.endswith(".csv")):
            continue
        filePath = path + filename
        fileDecisionModel = re.compile(r"^([A-z]*)(\d*)\.(json|csv)")
        fileSearch = re.search(fileDecisionModel, filename)
        if fileSearch == None:
            continue
        model = fileSearch.group(1)
        if model not in dataset:
            continue
        seed = fileSearch.group(2)
        log = open(filePath)
        print("Reading log {0}".format(filePath))
        rawData = None
        if filename.endswith(".json"):
            rawData = json.loads(log.read())
        else:
            rawData = list(csv.DictReader(log))

        if int(rawData[-1]["population"]) == 0:
            dataset[model]["died"] += 1
            if skipExtinct == True:
                continue
        elif int(rawData[-1]["population"]) <= int(rawData[0]["population"]):
            dataset[model]["worse"] += 1
        else:
            dataset[model]["better"] += 1

        dataset[model]["runs"] += 1
        i = 1
        for item in rawData:
            if int(item["timestep"]) > totalTimesteps:
                break
            if int(item["timestep"]) > dataset[model]["timesteps"]:
                dataset[model]["timesteps"] += 1

            for entry in item:
                if entry in ["agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited", "agentTotalMetabolism"]:
                    continue
                if entry not in dataset[model]["metrics"]:
                    if statistic == "mean":
                        dataset[model]["metrics"][entry] = [0 for j in range(totalTimesteps + 1)]
                    elif statistic == "median":
                        dataset[model]["metrics"][entry] = [[] for j in range(totalTimesteps + 1)]
                if item[entry] == "None":
                    item[entry] = 0
                if statistic == "mean":
                    dataset[model]["metrics"][entry][i-1] += float(item[entry])
                elif statistic == "median":
                    dataset[model]["metrics"][entry][i-1].append(float(item[entry]))
            i += 1
    for model in dataset:
        if dataset[model]["runs"] == 0:
            print(f"No simulation runs found for the {model} decision model")
    return dataset

def parseOptions():
    commandLineArgs = sys.argv[1:]
    shortOptions = "c:p:s:t:h"
    longOptions = ("conf=", "path=", "help", "skip")
    options = {"config": None, "path": None, "skip": False}
    try:
        args, vals = getopt.getopt(commandLineArgs, shortOptions, longOptions)
    except getopt.GetoptError as err:
        print(err)
        exit(0)
    for currArg, currVal in args:
        if currArg in ("-c", "--conf"):
            if currVal == "":
                print("No config file provided.")
                printHelp()
            options["config"] = currVal
        elif currArg in ("-p", "--path"):
            options["path"] = currVal
            if currVal == "":
                print("No dataset path provided.")
                printHelp()
        elif currArg in ("-h", "--help"):
            printHelp()
        elif currArg in ("-s", "--skip"):
            options["skip"] = True
    flag = 0
    if options["path"] == None:
        print("Dataset path required.")
        flag = 1
    if options["config"] == None:
        print("Configuration file path required.")
        flag = 1
    if flag == 1:
        printHelp()
    return options

def printHelp():
    print("Usage:\n\tpython plot.py --path /path/to/data --conf /path/to/config > results.dat\n\nOptions:\n\t-c,--conf\tUse the specified path to configurable settings file.\n\t-p,--path\tUse the specified path to find dataset JSON files.\n\t-s,--skip\tSkip including extinct societies in produced graphs.\n\t-h,--help\tDisplay this message.")
    exit(0)

def printSummaryStats(dataset):
    print("Model population performance:\n{0:^30} {1:^5} {2:^5} {3:^5}".format("Decision Model", "Extinct", "Worse", "Better"))
    for model in dataset:
        print("{0:^30}: {1:^5} {2:^5} {3:^5}".format(model, dataset[model]["died"], dataset[model]["worse"], dataset[model]["better"]))

if __name__ == "__main__":
    options = parseOptions()
    path = options["path"]
    config = options["config"]
    skipExtinct = options["skip"]
    configFile = open(config)
    config = json.loads(configFile.read())
    configFile.close()
    experimentalGroup = config["sugarscapeOptions"]["experimentalGroup"] if "experimentalGroup" in config["sugarscapeOptions"] else None
    config = config["dataCollectionOptions"]
    totalTimesteps = config["plotTimesteps"]
    models = config["decisionModels"]
    statistic = config["plotStatistic"]
    dataset = {}
    for model in models:
        modelString = model
        if type(model) == list:
            modelString = '_'.join(model)
        dataset[modelString] = {"runs": 0, "died": 0, "worse": 0, "better": 0, "timesteps": 0, "aggregates": {}, "firstQuartiles": {}, "thirdQuartiles": {}, "metrics": {}}

    if not os.path.exists(path):
        print(f"Path {path} not recognized.")
        printHelp()

    dataset = parseDataset(path, dataset, totalTimesteps, statistic, skipExtinct)
    if statistic == "mean":
        dataset = findMeans(dataset)
    elif statistic == "median":
        dataset = findMedians(dataset)
    else:
        print(f"Plotting statistic {statistic} not recognized.")
        printHelp()

    generatePlots(config, models, totalTimesteps, dataset, statistic, experimentalGroup)
    printSummaryStats(dataset)
    exit(0)
