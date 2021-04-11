
from PIL import Image
from pathlib import Path
from shutil import copyfile

# This method will merge together the images in the inputFolder! It
# assumes the images are 512x512 outputs from BigSleep.
def mergeImageFolder(inputFolder):

	# Open all of the images
	images = []
	for imageFile in inputFolder.iterdir():
		if (imageFile.name == "grid.png"): continue
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
	baseImage.save(str(inputFolder / Path("grid.png")))

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
def seedMerge(inputFolder):

	# Find the last picture in each of the seed folders
	lastPics = []
	for folder in inputFolder.iterdir():
		if (Path.is_dir(folder) and str(folder.name).startswith("seed ")):
			fileDict = {}
			for file in folder.iterdir():
				if (Path.is_dir(file)): continue
				if (file.stem == "starting"): continue
				fileDict[int(file.stem)] = file
			sortedFileList = [(k, v) for k,v in sorted(fileDict.items(), key=lambda item: item[0])]
			lastPics.append(sortedFileList[-1][1])

	# Create a new folder with each of the last pics
	newFolderPath = inputFolder / Path("Result Pics")
	if (not Path.exists(newFolderPath)):
		Path.mkdir(newFolderPath)
	for pic in lastPics:
		picSeed = " ".join(str(pic.parents[0].name).split()[1:])
		picName = picSeed + ".png"
		newPicDest = newFolderPath / Path(picName)
		if (not Path.exists(newPicDest)):
			copyfile(pic, newPicDest)

	mergeImageFolder(inputFolder / Path("Result Pics"))