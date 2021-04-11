

# Some import statements
from os import system
from time import sleep
from random import randint
from pathlib import Path
from otherScripts import seedPicMerge, mp4Maker

def runBigSleep(userInput, seed, learningRate, numImg, fps=None, skip=2):
	
	if (not Path.exists(Path("Output\\"))):
		Path.mkdir(Path("Output\\"))


	imgFolder = Path("Output\\" + userInput + "\\seed " + str(seed))

	seed = str(seed)
	learningRate = str(learningRate)
	numImg = str(numImg)
	ogUserInput = userInput
	userInput = "_".join(userInput.split())

	command = "python modularBigSleep.py " + seed + " " + learningRate + " " + numImg + " " + userInput + " " + str(skip)
	system(command)

	if (not Path.exists(Path("Output\\" + ogUserInput + "\\mp4s"))):
		Path.mkdir(Path("Output\\" + ogUserInput + "\\mp4s"))
	if (skip>1):
		mp4Maker.cleanResultPics(imgFolder)
	outputName = Path("Output\\" + ogUserInput + "\\mp4s\\" + seed + ".mp4")
	if (Path.exists(outputName)): 
		curVersion = 2
		outputName = Path(str(outputName)[:-4] + " v%d.mp4" % curVersion) 
		while (Path.exists(outputName)): 
			curVersion += 1
			outputName = Path(str(outputName)[:-4] + " v%d.mp4" % curVersion) 
	mp4Maker.img2mp4(imgFolder, "", outputFile=str(outputName), fps=fps)

	mainFolder = Path("Output\\" + ogUserInput)
	seedPicMerge.seedMerge(mainFolder)

def randomSeedRuns(phrase, amt=3, learnRate=0.055, amtPics=75, skipAmt=2, fps=None):
	seeds = []
	for seed in range(amt):
		seeds.append(randint(0, 999999999))
	for seed in seeds:
		runBigSleep(phrase, seed, learnRate, amtPics, skip=skipAmt, fps=fps)

	mainFolder = Path("Output\\" + phrase)
	mp4Maker.seedMP4(mainFolder, fps)

# This method will run "amt" runs, each starting at the same seed ("seed"). 
def sameSeedRuns(phrase, seed=0, amt=3, learnRate=0.055, amtPics=75, fps=None, skipAmt=2):
	seeds = []
	for seedNum in range(amt):
		seeds.append(seed)
	for curSeed in seeds:
		runBigSleep(phrase, curSeed, learnRate, amtPics, skip=skipAmt, fps=fps)

	mainFolder = Path("Output\\" + phrase)
	mp4Maker.seedMP4(mainFolder, fps)


phrases = ["soul eater", "diseased happiness", "brain tumor"]
phrases = [x.strip() for x in phrases]
for phrase in phrases:
	randomSeedRuns(phrase, amt=4, amtPics=100, learnRate=0.052, fps=10, skipAmt=1)

