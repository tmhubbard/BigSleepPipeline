
import imageio, os
from PIL import Image
from pathlib import Path
from shutil import copyfile, rmtree

# This method will merge together the images in the inputFolder! It
# assumes the images are 512x512 outputs from BigSleep.
def mergeImageFolder(inputFolder, picList, outputName):

	# Open all of the images
	images = []
	for imageFile in picList:
		images.append(Image.open(str(imageFile)))
	
	# Create the array we'll store the rows in 
	rows = []

	# If we've got 4 or less images, handle it this way
	if (len(images) <= 4):
		baseRow = createRow_4orLess(images)
		rows.append(baseRow)

	# This handles the other case (more than four images)
	elif(len(images) > 4):

		theRest = []
		leftoverImages = []
		if ((len(images)//4) >= 2):
			leftover = (len(images) % 4)
			if (leftover != 0):
				slicePoint = (-1*(4+leftover))
				theRest = images[:slicePoint]
				leftoverImages = images[slicePoint:]
			if (leftover == 0):
				theRest = images
		else:
			leftoverImages = images

		# Dealing with everything in theRest, which *should* be divisible by 4
		if (theRest):
			rowCount = int(len(theRest)/4)
			for rowIdx in range(rowCount):
				rowSlicePoint = 4 * rowIdx
				rowImages = theRest[rowSlicePoint:(rowSlicePoint+4)]
				rows.append(createRow_4orLess(rowImages))

		# Dealing with the leftoverImages
		# Deals w/ 5 and 6
		if (len(leftoverImages) == 5 or len(leftoverImages) == 6):
			firstRow = leftoverImages[:3]
			secondRow = leftoverImages[3:]
			rows.append(createRow_4orLess(firstRow))
			rows.append(createRow_4orLess(secondRow))

		# Deals w/ 7
		elif(len(leftoverImages) == 7):
			firstRow = leftoverImages[:4]
			secondRow = leftoverImages[4:]
			rows.append(createRow_4orLess(firstRow))
			rows.append(createRow_4orLess(secondRow))
	
	# Putting the rows together
	baseImage_height = (((64 + 512) * len(rows)) + 64)
	baseImage_width = 2368
	baseImage = Image.new('RGB', (baseImage_width, baseImage_height))
	for rowIdx, row in enumerate(reversed(rows)):
		pasteHeight =  (baseImage_height - 64) - ((64 + 512) * (rowIdx+1))
		baseImage.paste(im=row, box=(0, pasteHeight))
	baseImage.save(str(inputFolder / Path(outputName + ".png")))

# This helper method handles rows that're 4 or less images 
def createRow_4orLess(images):

	# Creating the baseRow image
	baseRow_width = 2368
	baseRow_height = 640
	baseRow = Image.new('RGB', (baseRow_width, baseRow_height))
	picWidth = 512

	# Handling the case where there's 1 image
	if (len(images) == 1):
		x = int((baseRow_width-(picWidth))/2)
		baseRow.paste(im=images[0], box=(x, 64))

	# Handling the case where there's 2 images
	elif (len(images) == 2):
		x = int((baseRow_width-(picWidth*2))/3)
		baseRow.paste(im=images[0], box=(x, 64))
		baseRow.paste(im=images[1], box=(((2*x)+picWidth), 64))

	# Handling the case where there's 3 images
	elif (len(images) == 3):
		x = int((baseRow_width-(picWidth*3))/4)
		baseRow.paste(im=images[0], box=(x, 64))
		baseRow.paste(im=images[1], box=(((2*x)+picWidth), 64))
		baseRow.paste(im=images[2], box=(((3*x)+(2*picWidth)), 64))

	# Handling the case where there's 4 images
	elif (len(images) == 4):
		x = int((baseRow_width-(picWidth*4))/5)
		baseRow.paste(im=images[0], box=(x, 64))
		baseRow.paste(im=images[1], box=(((2*x)+picWidth), 64))
		baseRow.paste(im=images[2], box=(((3*x)+(2*picWidth)), 64))
		baseRow.paste(im=images[3], box=(((4*x)+(3*picWidth)), 64))

	return baseRow

# This method will merge together the last pictures in each of the seed folders
def seedMP4(inputFolder, fps=None):

	# Find the last picture in each of the seed folders
	picTraces = []
	for folder in inputFolder.iterdir():
		if (Path.is_dir(folder) and str(folder.name).startswith("seed ")):
			fileDict = {}
			for file in folder.iterdir():
				if (Path.is_dir(file)): continue
				if (file.stem == "starting"): continue
				fileDict[int(file.stem)] = file
			sortedFileList = [(k, v) for k,v in sorted(fileDict.items(), key=lambda item: item[0])]
			picTraces.append(sortedFileList)

	numFolders = {}
	for curTrace in picTraces:
		for picNum, picPath in curTrace:
			if (picNum not in numFolders):
				numFolders[picNum] = []
			numFolders[picNum].append(picPath)

	# Pass the paths to the images themselves
	if (not Path.is_dir(inputFolder / Path("GridMerge"))):
		Path.mkdir(inputFolder / Path("GridMerge"))

	for picNum, folderList in numFolders.items():
		print("Creating the grid for pic %d" % picNum)
		mergeImageFolder(inputFolder / Path("GridMerge"), folderList, str(picNum))

	print("\nCreating the GIF...")

	# Cleaning the GridMerge folder
	cleanResultPics(str(inputFolder / Path("GridMerge")))

	img2mp4((inputFolder / Path("GridMerge")), Path(inputFolder).stem, fps=fps)

	rmtree(Path(inputFolder / Path("GridMerge")))

# This will ensure that all of the pictures are named correctly
def cleanResultPics(resultFolder):

	resultFolderPath = Path(resultFolder)
	fileDict = {}
	for resultFile in resultFolderPath.iterdir():
		if (resultFile.stem == "starting"): continue
		resultNum = int(resultFile.stem)
		fileDict[resultNum] = resultFile

	# Iterate through the sorted fileDict and create new names
	imagePathDict = {k: v for k, v in sorted(fileDict.items(), key=lambda item: item[0])}
	curPicNum = 0
	for picNum, picPath in imagePathDict.items():

		newName = picPath.parents[0] / Path(str(curPicNum) + ".png")
		picPath.rename(newName)

		curPicNum += 1

def collectResultGrids(resultFolder):

	# Figure out the paths to all of the pics
	picPaths = []
	folderPaths = []
	for folder in resultFolder.iterdir():
		folderPaths.append(folder)
		print(folder)
		picPaths.append(folder / Path(folder.stem + ".png"))
	
	# Copy all of the pics to resultFolder
	for pic in picPaths:
		newDest = resultFolder / Path(pic.stem + ".png")
		copyfile(pic, newDest)

	# Delete all of the intermediate folders
	for folder in folderPaths:
		rmtree(folder)

def img2mp4(inFolder, filename, outputFile=None, fps=None):

	if (fps is None):
		fileCt = 0
		# Count how many files are in the infolder
		for file in Path(inFolder).iterdir():
			fileCt += 1
		fps = int(fileCt/7)
		if (fps==0): fps=1

	if (outputFile is None):
		outputFile = str(Path(inFolder).parents[0]) + "\\" + filename + ".mp4"
	command = "ffmpeg -r %d -f image2 -s 1280x720 -i \"%s/%%d.png\" -vcodec libx264 -crf 25  -pix_fmt yuv420p \"%s\"" % (fps, inFolder, outputFile)
	print(command)
	os.system(command)
