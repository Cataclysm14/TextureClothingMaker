import os
import shutil
import json
import re
from PIL import Image #in cmd enter "py -m pip download pillow" + "py -m pip install pillow", works for me, probably not on other devices :godo:

def colorReplace(img,color=(255,0,0,255)):
    #Too lazy to use channels.
    img_pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if img_pixels[x,y] == (255,0,0,255):
                img_pixels[x,y] = (0,0,0,0)
    return img

def removeAlpha(img):
    #Too lazy to use channels.
    img_pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if img_pixels[x,y][3] != 255 and not img_pixels[x,y][3] == 0:
                img_pixels[x,y] = (img_pixels[x,y][0],img_pixels[x,y][1],img_pixels[x,y][2],255)
    return img

def overlayImg(img,mask,offset=(0,0)):
    img.paste(mask, (offset[0],-offset[1]), mask)
    return img

def exportClothings(dumpFiles=False):

    camoList = os.listdir("Textures")
    camoDirs = []
    for camo in camoList:
        camo = camo.replace(".png","")
        camo = re.sub(r"(^|_)([a-z])", lambda match: match.group(2).upper(), camo)
        camoDirs.append(camo)

    #Get a list of every template folders.
    templateList = [x[0] for x in os.walk("Templates")]
    templateList.pop(0)
    templateList = [x.replace("Templates\\","") for x in templateList]

    for camoIndex in range(len(camoList)):
        if dumpFiles:
            camo = camoList[camoIndex]
            camoPath = ""
            camoImg = Image.open("Textures/"+camo)
        else:
            camo = camoList[camoIndex]
            camoPath = camoDirs[camoIndex]
            camoImg = Image.open("Textures/"+camo)

            os.mkdir("Outputs/"+camoPath)
        
        camo = camo.replace(".png","")
        for clothing in templateList:
            #Make the dir and save names.
            template_directory_name = "Templates/"+clothing
        
            #Save the dict relating to this clothing.
            clothing_values = json.load(open(template_directory_name+"/params.json"))

            #Save output dirs
            outputs_directory_name = str("Outputs/"+clothing_values["path"]+"/"+camoPath+"/"+clothing).replace("CamoName",camo)

            #Create type dir
            if not os.path.isdir(str("Outputs/"+clothing_values["path"])):
                os.mkdir(str("Outputs/"+clothing_values["path"]))

            #Create camo dir
            os.mkdir(outputs_directory_name)

            #Copy the meta.json.
            shutil.copy(template_directory_name+"/meta.json",outputs_directory_name)
            
            #Apply mask and shading
            mask = Image.open(template_directory_name+"/equipped-"+clothing_values["type"]+"_mask.png")
            shading = Image.open(template_directory_name+"/equipped-"+clothing_values["type"]+"_shading.png")

            img = camoImg
            img = overlayImg(img,mask)
            img = overlayImg(img,shading)
            img = colorReplace(img)
            img = removeAlpha(img)
            img.save(outputs_directory_name+"/equipped-"+clothing_values["type"]+".png")

            frontSprite = img.crop((0,0,32,32))
            backSprite = img.crop((32,0,64,32))

            #icon
            icon = Image.new("RGBA",(32,32))
            offset = (
                clothing_values["frontAnchor"][0]-clothing_values["iconOffset"][0],
                clothing_values["frontAnchor"][1]-clothing_values["iconOffset"][1]
                )
            icon = overlayImg(icon,frontSprite,offset)
            icon.save(outputs_directory_name+"/icon"+".png")

            #inhand-left
            inhandLeft = Image.new("RGBA",(64,64))
            for direction in clothing_values["inhandLeftOffset"]:
                if direction[2] == "front":
                    offset = (
                        direction[0]-clothing_values["frontAnchor"][0],
                        -(direction[1]-clothing_values["frontAnchor"][1])
                        )
                    sprite = frontSprite
                else:
                    offset = (
                        direction[0]-clothing_values["backAnchor"][0],
                        -(direction[1]-clothing_values["backAnchor"][1])
                        )
                    sprite = backSprite
                inhandLeft = overlayImg(inhandLeft,sprite,offset)
            inhandLeft.save(outputs_directory_name+"/inhand-left"+".png")
            
            #inhand-right
            inhandRight = Image.new("RGBA",(64,64))
            for direction in clothing_values["inhandRightOffset"]:
                if direction[2] == "front":
                    offset = (
                        direction[0]-clothing_values["frontAnchor"][0],
                        -(direction[1]-clothing_values["frontAnchor"][1])
                        )
                    sprite = frontSprite
                else:
                    offset = (
                        direction[0]-clothing_values["backAnchor"][0],
                        -(direction[1]-clothing_values["backAnchor"][1])
                        )
                    sprite = backSprite
                inhandRight = overlayImg(inhandRight,sprite,offset)
            inhandRight.save(outputs_directory_name+"/inhand-right"+".png")

shutil.rmtree("Outputs")
os.mkdir("Outputs")

dumpToggle = input("Dump files?: Y/N >> ")
if "Y" in  dumpToggle:
    dumpToggle = True
else: dumpToggle = False
exportClothings(dumpToggle)

# while 0 != 1:
#     a = 1   