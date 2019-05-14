__author__ = 'sojasasi'

import bpy
import math
import sqlite3

#Create material and its properties- colour, shading
class MaterialObject:
    def __init__(self, material_name,r,g,b, isTransparent):
        self.name = material_name    
        self.materialObj = bpy.data.materials.new(name=material_name)
        self.materialObj.diffuse_color = (r,g,b)
        self.materialObj.use_shadeless = True
        self.materialObj.use_object_color = True
        self.materialObj.use_transparency = isTransparent
        self.materialObj.alpha = 0.1
        
    def getMaterial(self):
        return self.materialObj


class BasicObject:
    def __init__(self,name,location_x,location_y,location_z):
        self.name = name
        self.location = [location_x,location_y,location_z]
   
    def getName(self):
        return self.name

    def createPlane(self, dim_x, dim_y, dim_z):
        bpy.ops.mesh.primitive_plane_add(location=(self.location[0], self.location[1], self.location[2]))
        self.planeObj = bpy.context.object
        self.planeObj.name = self.getName()
        self.planeObj.dimensions = (dim_x, dim_y, dim_z)

    def getBasePlane(self):
        return self.planeObj

    def addMaterialToObject(self, material_name, r, g, b, isTransparent):
        sampleMaterial = MaterialObject(material_name, r, g, b, isTransparent)
        self.planeObj.data.materials.append(sampleMaterial.getMaterial())

    def addTextureToObject(self, material_name, texture_filename, texture_name, isTransparent):
        greyMaterial = MaterialObject(material_name, 0.1, 0.1, 0.1, isTransparent)
        self.planeObj.data.materials.append(greyMaterial.getMaterial())
        textureImg = bpy.data.images.load(texture_filename)
        givenTexture = bpy.data.textures.new(texture_name, 'IMAGE')
        givenTexture.image = textureImg
        self.planeObj.data.materials[material_name].active_texture = givenTexture

        bpy.ops.object.select_all(action='DESELECT') 
        self.planeObj.select = True
        bpy.data.scenes['Menu'].objects.active = self.planeObj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001) 
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)  

    def linkSensorAndController(self, sensor, controller):
        bpy.data.objects[self.name].game.sensors[sensor].link(bpy.data.objects[self.name].game.controllers[controller])    
     
    def linkActuatorAndController(self, actuator, controller):
        bpy.data.objects[self.name].game.actuators[actuator].link(bpy.data.objects[self.name].game.controllers[controller])

    def addController(self, type, controller_name):
        bpy.ops.logic.controller_add(type=type, name = controller_name, object=self.name)    

    def addMessageSensor(self, message):
        bpy.ops.logic.sensor_add(type='MESSAGE',name = message, object=self.name)
        bpy.data.objects[self.name].game.sensors[message].subject = message

    def addMouseSensor(self, sensor_name, event, invert):
        bpy.ops.logic.sensor_add(type='MOUSE',name = sensor_name, object=self.name)
        bpy.data.objects[self.name].game.sensors[sensor_name].mouse_event = event        
        bpy.data.objects[self.name].game.sensors[sensor_name].invert = invert
    
    def addMessageActuator(self, actuator_name, message, to_object=''):
        bpy.ops.logic.actuator_add(type='MESSAGE', name= actuator_name, object=self.name)
        bpy.data.objects[self.name].game.actuators[actuator_name].subject = message
        if not to_object:
            bpy.data.objects[self.name].game.actuators[actuator_name].to_property = to_object

    def addActionActuator(self, actuator_name, fstart, fend, actionName):
        bpy.ops.logic.actuator_add(type='ACTION', name= actuator_name, object=self.name) 
        bpy.data.objects[self.name].game.actuators[actuator_name].frame_end = fend
        bpy.data.objects[self.name].game.actuators[actuator_name].frame_start = fstart
        bpy.data.objects[self.name].game.actuators[actuator_name].action = bpy.data.actions[actionName]
        
    def addSetParentActuator(self, actuator_name, parent_obj):
        bpy.ops.logic.actuator_add(type='PARENT', name= actuator_name, object=self.name) 
        bpy.data.objects[self.name].game.actuators[actuator_name].object = bpy.data.objects[parent_obj]         

    def addEditObjectActuator(self, actuator_name, edit_self, mode):
        bpy.ops.logic.actuator_add(type='EDIT_OBJECT', name= actuator_name, object=self.name) 
        bpy.data.objects[self.name].game.actuators[actuator_name].object = bpy.data.objects[edit_obj]
        bpy.data.objects[self.name].game.actuators[actuator_name].mode = mode 

    def addSetSceneActuator(self, sceneId):
        bpy.ops.logic.actuator_add(type='SCENE', object=self.name) 
        bpy.data.objects[self.name].game.actuators['Scene'].mode = 'SET'
        bpy.data.objects[self.name].game.actuators['Scene'].scene = bpy.data.scenes[sceneId]

    def addAlwaysSensor(self, sensor_name):
        bpy.ops.logic.sensor_add(type='ALWAYS', name = sensor_name, object=self.name)
        bpy.data.objects[self.name].game.sensors[sensor_name].use_pulse_true_level = True

    def addPythonController(self, controller_name, script):
        filepathstr = homeDir + sourceDir + script
        bpy.ops.text.open(filepath=filepathstr)
        bpy.ops.logic.controller_add(type='PYTHON', object=self.name, name = controller_name)
        bpy.data.objects[self.name].game.controllers[controller_name].text = bpy.data.texts[script]

class Button(BasicObject):
    def __init__(self, name, x, y, z, size, length):
        objectName = 'button' + name.lower() 
        super().__init__(objectName,x,y,z)
        self.text = name       
        super().createPlane(length,0.7,0) #dimensions
        self.addText(size)

    def getButtonObject(self,size,length):
        return self
        
    def addText(self,size):
        myFontCurve = bpy.data.curves.new(type="FONT",name = "button_text")
        self.buttonName = 'text'+ self.getName()
        self.buttonObj = bpy.data.objects.new(self.buttonName,myFontCurve)
        self.buttonObj.data.body = self.text.upper()
        self.buttonObj.data.size = size
        bpy.context.scene.objects.link(self.buttonObj)
        self.buttonObj.select = True
        bpy.data.scenes['Menu'].objects.active = self.buttonObj
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
        fnt = bpy.data.fonts.load('/usr/share/fonts/opentype/cabin/Cabin-SemiBold.otf')
        self.buttonObj.data.font = fnt
        self.buttonObj.color = (0.8,0.8,0.8,1)
        self.buttonObj.location = self.location
        self.buttonObj.select = True
        super().getBasePlane().select = True
        bpy.data.scenes['Menu'].objects.active = super().getBasePlane()
        bpy.ops.object.parent_set()

    def addBlinkEffect(self):
        planeObj = super().getBasePlane()
        planeObj.color = (0.2,0.2,0.2,0.7)
        planeObj.keyframe_insert(data_path="color", frame=1)
        planeObj.color = (0.75,0.318,0.059,0.7)
        planeObj.keyframe_insert(data_path="color", frame=2)

        startFrame = 1
        endFrame = 2
        actionName = self.getName() + 'Action'
        super().addMouseSensor("mo", 'MOUSEOVER', False)
        super().addMouseSensor("mo_invert", 'MOUSEOVER', True)
        super().addController('LOGIC_AND',"and1") 
        super().addController('LOGIC_AND',"and2")
        super().addActionActuator("action1", endFrame, endFrame, actionName)
        super().addActionActuator("action2", startFrame, startFrame, actionName)
        super().linkSensorAndController("mo", "and1")
        super().linkSensorAndController("mo_invert", "and2")
        super().linkActuatorAndController("action1", "and1")
        super().linkActuatorAndController("action2", "and2") 

    def sendMessageOnLeftClick(self, messageActuatorId, messageContent):
        super().addMouseSensor('mleft', 'LEFTCLICK', False)
        super().addMessageActuator(messageActuatorId,messageContent)
        super().addController('LOGIC_AND','and3')
        super().linkSensorAndController('mleft','and3')
        super().linkSensorAndController('mo','and3')
        super().linkActuatorAndController(messageActuatorId,'and3')

    def getPlaneObject(self):
        return super().getBasePlane()

class PaneObject(BasicObject):
    def __init__(self, name, x, y, z, dim_x, dim_y):
        objectName = 'pane' + name.lower() 
        super().__init__(objectName, x, y, z)
        super().createPlane(dim_x, dim_y, 0)
        #super().addMaterialToObject('basicGray', 0.1, 0.1, 0.1, True)
        fname = homeDir + resourceDir + "Gradient.png"
        super().addTextureToObject('basicGray',fname,'gradient',True)

    def getPlaneObject(self):
        return super().getBasePlane()

    def addButton(self, buttonName, loc_x, loc_y, loc_z, textsize, planesize, blink, link):
        print('Creating Button for ',name)
        myButtonProject = Button(buttonName, loc_x, loc_y, loc_z, textsize, planesize)
        buttonVar = myButtonProject.getButtonObject()
        myButtonProject.addMaterialToPlane(greyMaterialObj)
        if blink == True:
            myButtonProject.addBlinkEffect()
        planeObj = super().getBasePlane()
        setParent(0, planeObj, buttonVar.getBasePlane())
        if link == True:
            buttonVar.sendMessageOnLeftClick()
            #addLinkToProjects(stringVal, buttonVar.planeObj)


def setParent(parent, child):
    bpy.ops.object.select_all(action='DESELECT') 
    parent.select = True
    child.select = True
    bpy.data.scenes['Menu'].objects.active = parent
    #bpy.data.objects[child].parent = bpy.data.objects[parent]
    bpy.ops.object.parent_set()



#Initial settings
bpy.context.scene.name = 'Menu'
bpy.context.scene.render.engine = 'BLENDER_GAME'
homeDir =  "/home/soja/Desktop/Task1/"
resourceDir = "resources/"
sourceDir = "src/"

currentScene = bpy.data.scenes['Menu']
bpy.ops.object.lamp_add(type='POINT', radius=2, location=(-6, -5, -5))

db_filename = homeDir + sourceDir + 'db/visionlab.db'

conn = sqlite3.connect(db_filename) 
cursor = conn.cursor()

lsp =  PaneObject('LeftSidePlane',-8,0,0,7,13)
hspace = 2
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    str = ''.join(row)
    if str != 'sqlite_sequence':
        myButtonProject = Button(str, -8, hspace, 0.4, 0.6, 6)
        hspace = hspace - 1
        bP = myButtonProject.getButtonObject()
        myButtonProject.addBlinkEffect()
        setParent(lsp.getPlaneObject(), bP.getPlaneObject())

