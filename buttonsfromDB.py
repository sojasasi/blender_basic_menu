import sqlite3
import bpy
import math

#Create material and its properties- colour, shading
def createMaterial(name,r,g,b):
        mat_obj = bpy.data.materials.new(name=name)
        mat_obj.diffuse_color = (r,g,b)
        mat_obj.use_shadeless = True
        mat_obj.use_object_color = True
        return mat_obj 

#Class to create Buttons for each item
#The text is given a rectangle background and parented to it.
#Each button has a blinking effect when mouse cursor is hovered upon it
class Button:
    def __init__(self,name,x,y,z):
        self.name = name
        self.location = [x,y,z]        

    def create(self,layer,size,length):
        self.layer = layer;
        self.createPlane(length)
        self.addText(size)
        return self
        
    def createPlane(self, length):
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(self.location[0], self.location[1], self.location[2]), \
								 layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        self.planeObj = bpy.context.object
        self.planeObj.name = 'p'+ self.name.lower()
        self.planeObj.layers = [ i == self.layer for i in range(len(self.planeObj.layers)) ] 
        self.planeObj.dimensions = (length,0.7,0)
        #self.planeObj.rotation_euler = (0,3.14*6/180,0)
        
    def addText(self,size):
        myFontCurve = bpy.data.curves.new(type="FONT",name = "button_text")
        self.buttonName = 'b'+ self.name.lower()
        self.buttonObj = bpy.data.objects.new(self.buttonName,myFontCurve)
        self.buttonObj.data.body = self.name.upper()
        self.buttonObj.data.size = size
        bpy.context.scene.objects.link(self.buttonObj)
        self.buttonObj.select = True
        bpy.data.scenes['Menu'].objects.active = self.buttonObj
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
        self.buttonObj.layers = [ i == self.layer for i in range(len(self.buttonObj.layers)) ] 
        fnt = bpy.data.fonts.load('/usr/share/fonts/opentype/cabin/Cabin-SemiBold.otf')
        self.buttonObj.data.font = fnt
        self.buttonObj.color = (0.8,0.8,0.8,1)
        self.buttonObj.location = self.location
        #self.buttonObj.rotation_euler = (0,3.14*6/180,0)
        if bpy.data.scenes['Menu'].layers[self.layer] == True:
            self.buttonObj.select = True
            self.planeObj .select = True
            bpy.data.scenes['Menu'].objects.active = self.planeObj
            bpy.ops.object.parent_set()
        else:
            bpy.data.scenes['Menu'].layers[self.layer] = True
            bpy.ops.object.select_all(action='DESELECT') 
            self.buttonObj.select = True
            self.planeObj .select = True
            bpy.data.scenes['Menu'].objects.active = self.planeObj 
            bpy.ops.object.parent_set()
            bpy.data.scenes['Menu'].layers[self.layer] = False
        #bpy.data.objects[self.buttonName].parent = bpy.data.objects[self.planeObj.name]
        
    def addMaterialToPlane(self, matObj):
        self.planeObj.data.materials.append(matObj)

    def addBlinkEffect(self):
        self.planeObj.color = (0.2,0.2,0.2,0.7)
        self.planeObj.keyframe_insert(data_path="color", frame=1)
        self.planeObj.color = (0.75,0.318,0.059,0.7)
        self.planeObj.keyframe_insert(data_path="color", frame=2)
        bpy.ops.logic.sensor_add(type='MOUSE',name = "mo", object=self.planeObj.name)
        bpy.data.objects[self.planeObj.name].game.sensors['mo'].mouse_event = 'MOUSEOVER'
        bpy.ops.logic.sensor_add(type='MOUSE',name = "ml", object=self.planeObj.name)
        bpy.data.objects[self.planeObj.name].game.sensors['ml'].mouse_event = 'MOUSEOVER'       
        bpy.data.objects[self.planeObj.name].game.sensors['ml'].invert = True
        bpy.ops.logic.controller_add(type='LOGIC_AND', name = "and1", object=self.planeObj.name)
        bpy.ops.logic.actuator_add(type='ACTION', name= "action1", object=self.planeObj.name) 
        bpy.ops.logic.controller_add(type='LOGIC_AND', name = "and2", object=self.planeObj.name)
        bpy.ops.logic.actuator_add(type='ACTION', name= "action2", object=self.planeObj.name)
        sensors = bpy.data.objects[self.planeObj.name].game.sensors
        actuators = bpy.data.objects[self.planeObj.name].game.actuators
        sensors['mo'].link(bpy.data.objects[self.planeObj.name].game.controllers['and1'])
        sensors['ml'].link(bpy.data.objects[self.planeObj.name].game.controllers['and2'])
        actuators['action1'].link(bpy.data.objects[self.planeObj.name].game.controllers['and1'])
        actuators['action2'].link(bpy.data.objects[self.planeObj.name].game.controllers['and2'])
        actuators['action1'].frame_start = 2
        actuators['action1'].frame_end = 2
        actuators['action2'].frame_start = 1
        actuators['action2'].frame_end = 1
        actionName = self.planeObj.name + 'Action'
        actuators['action1'].action = bpy.data.actions[actionName]
        actuators['action2'].action = bpy.data.actions[actionName]
#################

#Logic Editor 
#Sensors, Actuators, Controllers
def addMessageSensor(obj,message):
    bpy.ops.logic.sensor_add(type='MESSAGE',name = message, object=obj)
    bpy.data.objects[obj].game.sensors[message].subject = message

def addMouseSensor(obj,name,event,invert):
    bpy.ops.logic.sensor_add(type='MOUSE',name = name, object=obj)
    bpy.data.objects[obj].game.sensors[name].mouse_event = event        
    bpy.data.objects[obj].game.sensors[name].invert = invert
    
def addMessageActuator(obj,name,message,to_object=''):
    bpy.ops.logic.actuator_add(type='MESSAGE', name= name, object=obj)
    bpy.data.objects[obj].game.actuators[name].subject = message
    if not to_object:
        bpy.data.objects[obj].game.actuators[name].to_property = to_object

def addActionActuator(obj,name,fstart,fend,actionName):
    bpy.ops.logic.actuator_add(type='ACTION', name= name, object=obj) 
    bpy.data.objects[obj].game.actuators[name].frame_end = fend
    bpy.data.objects[obj].game.actuators[name].frame_start = fstart
    bpy.data.objects[obj].game.actuators[name].action = bpy.data.actions[actionName]
        
def addSetParentActuator(obj, name, parent_obj):
    bpy.ops.logic.actuator_add(type='PARENT', name= name, object=obj) 
    bpy.data.objects[obj].game.actuators[name].object = bpy.data.objects[parent_obj]         

def addEditObjectActuator(obj,name, edit_obj, mode):
    bpy.ops.logic.actuator_add(type='EDIT_OBJECT', name= name, object=obj) 
    bpy.data.objects[obj].game.actuators[name].object = bpy.data.objects[edit_obj]
    bpy.data.objects[obj].game.actuators[name].mode = mode 

def addSetSceneActuator(obj, sceneId):
    bpy.ops.logic.actuator_add(type='SCENE', object=obj) 
    bpy.data.objects[obj].game.actuators['Scene'].mode = 'SET'
    bpy.data.objects[obj].game.actuators['Scene'].scene = bpy.data.scenes[sceneId]

def addAlwaysSensor(obj,name):
    bpy.ops.logic.sensor_add(type='ALWAYS', name = name, object=obj)
    bpy.data.objects[obj].game.sensors[name].use_pulse_true_level = True

def addPythonController(obj,name,script):
    filepathstr = homeDir + sourceDir + script
    bpy.ops.text.open(filepath=filepathstr)
    bpy.ops.logic.controller_add(type='PYTHON', object=obj, name = name)
    bpy.data.objects[obj].game.controllers[name].text = bpy.data.texts[script]

def addActuator(type,obj,name):
     bpy.ops.logic.actuator_add(type=type, name= name, object=obj) 

def addController(type,obj,name):
    bpy.ops.logic.controller_add(type=type, name = name, object=obj)       		

def linkSensorAndController(obj, sensor, controller):
     bpy.data.objects[obj].game.sensors[sensor].link(bpy.data.objects[obj].game.controllers[controller])    
     
def linkActuatorAndController(obj, actuator, controller):
     bpy.data.objects[obj].game.actuators[actuator].link(bpy.data.objects[obj].game.controllers[controller])

########################################

def createSidePane(name,layer,x,y,z,dx,dy,dz):
    bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(x,y,z), \
    								 layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    sidePlane = bpy.context.object
    sidePlane.name = name
    sidePlane.layers = [ i == layer for i in range(len(sidePlane.layers)) ] 
    sidePlane.dimensions = (dx,dy,dz)
    #bpy.data.objects[name].game.physics_type = 'NO_COLLISION'
    return sidePlane

def setParent(layer,parent,child):
    if bpy.data.scenes['Menu'].layers[layer] == True:
        bpy.ops.object.select_all(action='DESELECT') 
        parent.select = True
        child.select = True
        bpy.data.scenes['Menu'].objects.active = parent
        #bpy.data.objects[child].parent = bpy.data.objects[parent]
        bpy.ops.object.parent_set()
    else:
        bpy.data.scenes['Menu'].layers[layer] = True
        bpy.ops.object.select_all(action='DESELECT') 
        parent.select = True
        child.select = True
        bpy.data.scenes['Menu'].objects.active = parent
        #bpy.data.objects[child].parent = bpy.data.objects[parent]
        bpy.ops.object.parent_set()
        bpy.data.scenes['Menu'].layers[layer] = False

def createButton(name,valx,valy,valz,layer,textsize,planesize,planeObj,blink = True,link=False):
    print('Creating Button for ',name)
    stringVal = ''.join(name)
    myButtonProject = Button(stringVal,valx,valy,valz)
    buttonVar = myButtonProject.create(layer,textsize,planesize)
    myButtonProject.addMaterialToPlane(greyMaterialObj)
    if blink == True:
            myButtonProject.addBlinkEffect()
    setParent(0, planeObj, buttonVar.planeObj)
    if link == True:
        addLinkToProjects(stringVal, buttonVar.planeObj)
        
def createEmptyObject(name,layer,type,x,y,z):
    bpy.ops.object.empty_add(type=type, view_align=False, location=(x,y,z), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    emptyObject = bpy.context.object
    emptyObject.name = name
    emptyObject.layers = [ i == layer for i in range(len(emptyObject.layers)) ]   
    return emptyObject

#Add texture to material from a given picture -- UV editing
#obj - Object to which texture is applied, fname - path of the pictur
def addMaterialForTexture(fname):
    img = bpy.data.images.load(fname)
    tex = bpy.data.textures.new('Tex1', 'IMAGE')
    tex.image = img
    mat = bpy.data.materials.new('Mat1')
    mat.use_transparency = True
    mat.alpha = 0
    mat.texture_slots.add()
    ts = mat.texture_slots[0]
    ts.texture = tex
    ts.use_map_alpha = True
    ts.texture_coords = 'UV'
    ts.uv_layer = 'default'
    return mat

#Add texture to material from a given picture
#obj - Object to which texture is applied, fname - path of the picture
def addTexture(obj, fname, layer, textureMat):
    islayerFalse = False
    if bpy.data.scenes['Menu'].layers[layer] == False:
        islayerFalse = True
        bpy.data.scenes['Menu'].layers[layer] = True
    bpy.ops.object.select_all(action='DESELECT') 
    obj.select = True
    bpy.data.scenes['Menu'].objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    obj.data.materials.append(textureMat)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    if islayerFalse == True:
        bpy.data.scenes['Menu'].layers[layer] = False

def addTextureToObject(mat_name, texture_filename, texture_name, testobject):
    mat_obj = bpy.data.materials.new(mat_name)
    mat_obj.diffuse_color = (0.1,0.1,0.1)
    mat_obj.use_shadeless = True
    mat_obj.use_object_color = True
    testobject.data.materials.append(mat_obj)
    img = bpy.data.images.load(texture_filename)
    givenTexture = bpy.data.textures.new(texture_name, 'IMAGE')
    givenTexture.image = img
    testobject.data.materials[mat_name].active_texture = givenTexture

    bpy.ops.object.select_all(action='DESELECT') 
    testobject.select = True
    bpy.data.scenes['Menu'].objects.active = testobject
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001) 
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)  
        
def addLinkToProjects(stringVal, planeObj):
    attachMessage = 'attachDesc' + stringVal
    slideMessage = 'slideDesc' + stringVal 
    andController = planeObj.name + 'and'
    planeId = stringVal + 'Plane'
    handleId = 'projectHandle'
    descPlaneObj = stringVal + 'descPlane' 
      
    downSlideHandleId = planeId + 'DownHandle'
    ePlainObj = createEmptyObject(downSlideHandleId, 0, 'PLAIN_AXES', 0,0,0)
    setParent(0, ePlainObj, bpy.data.objects[descPlaneObj]) 
     
    ePlainObj.location = (0,0,0)
    ePlainObj.keyframe_insert(data_path="location", frame=21)
    ePlainObj.location = (0,-14,0)
    ePlainObj.keyframe_insert(data_path="location", frame=35)

    addMouseSensor(planeObj.name, 'mleft', 'LEFTCLICK', False)
    addMessageActuator(planeObj.name, 'attachDescMessage',attachMessage)
    addController('LOGIC_AND',planeObj.name,'and3')
    linkSensorAndController(planeObj.name,'mleft','and3')
    linkSensorAndController(planeObj.name,'mo','and3')
    linkActuatorAndController(planeObj.name,'attachDescMessage','and3')

    downActionName = downSlideHandleId + 'Action'
    andController = 'and1' + stringVal
    slideDownMessage = 'slideDesc' + stringVal 
    backUpMessage =  stringVal + 'BackUpMessage'
    slidingAction = 'slidingAction' + stringVal
        
    addMessageSensor(downSlideHandleId,slideDownMessage);
    addController('LOGIC_AND',downSlideHandleId,andController)
    addActionActuator(downSlideHandleId,slidingAction,21,35,downActionName)
    linkSensorAndController(downSlideHandleId,slideDownMessage,andController)
    linkActuatorAndController(downSlideHandleId,slidingAction,andController)
                 
    and2Controller = 'and2' + stringVal
    backAction = 'backAction' + stringVal

    addMessageSensor(downSlideHandleId,backUpMessage);
    addController('LOGIC_AND',downSlideHandleId,and2Controller)    
    addActionActuator(downSlideHandleId,backAction,35,21,downActionName)
    linkSensorAndController(downSlideHandleId,backUpMessage,and2Controller)
    linkActuatorAndController(downSlideHandleId,backAction,and2Controller)

def addIconsToProjects(item, planeObj,locx,locy,locz):
    verts = []
    faces = []
    edges = []
    max = 10
    inc = (2*math.pi)/max
    a = 1
    b = 1
    c = 1
    u = 0
    v = 0
    if item == 'JobNet 4.0':
         print("created icon jobent")
         for i in range (0, max + 1):
             for j in range (0, max+1):
                 x = pow(a*math.cos(u)*math.cos(v),3)
                 y = pow(b*math.sin(u)*math.cos(v),3)
                 z = pow(c*math.sin(v),3)
 
                 vert = (x,y,z) 
                 verts.append(vert)
        
                 v = v + inc
             u = u + inc

    elif item == 'RealCoE':
         a = 0.2
         b = 0.6
         c = 0.3
         print("created icon Realcoe")
         for i in range (0, max + 1):
             for j in range (0, max+1):
                 x = a*math.cos(u)
                 y = b*math.cos(v) + a*math.sin(u)
                 z = c*math.sin(v)
 
                 vert = (x,y,z) 
                 verts.append(vert)
        
                 v = v + inc
             u = u + inc  
    elif item == 'SKILLS':
         a = 0.5
         b = 1
         c = 0.7
         u = -1*math.pi
         v = -1*math.pi
         print("created icon SKILLS")
         for i in range (0, max + 1):
             for j in range (0, max+1):
                 x = a*math.sin(u)*math.sin(v)
                 y = b*math.cos(u)*math.sin(v)
                 z = c*math.cos(u)*math.cos(v)
 
                 vert = (x,y,z) 
                 verts.append(vert)
        
                 v = v + inc
             u = u + inc  
        
    else:
        print("Invalid Project")

    count = 0
    for i in range (0, (max + 1) *(max)):
        if count < max:
            A = i
            B = i+1
            C = (i+(max+1))+1
            D = (i+(max+1))
 
            face = (A,B,C,D)
            faces.append(face)
 
            count = count + 1
        else:
            count = 0
        
    #create mesh and object
    name = item + 'icon'
    mymesh = bpy.data.meshes.new(name)
    myobject = bpy.data.objects.new(name,mymesh)
 
    #set mesh location
    myobject.location = (locx,locy,locz)
    bpy.context.scene.objects.link(myobject)
    
    #create mesh from python data
    mymesh.from_pydata(verts,edges,faces)
    mymesh.update(calc_edges=True)

    #set the object to edit mode
    bpy.context.scene.objects.active = myobject
    bpy.ops.object.mode_set(mode='EDIT')
 
    # remove duplicate vertices
    bpy.ops.mesh.remove_doubles() 

    # recalculate normals
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
 
    # subdivide modifier
    myobject.modifiers.new("subd", type='SUBSURF')
    myobject.modifiers['subd'].levels = 3
 
    # show mesh as smooth
    mypolys = mymesh.polygons
    for p in mypolys:
        p.use_smooth = True
    setParent(0, planeObj, myobject)
    addAlwaysSensor(name,'always')
    addPythonController(name,'rpy',"rotate.py")
    #linkSensorAndController(name,'always','rpy')
    
        
def createPanesForItem(item,stringVal,x,y,z,dx,dy,dz,hspace):
   #Create background plane
    planeId = stringVal + 'Plane'
    planeObj = createSidePane(planeId,0,x,y,z,dx,dy,dz)
    addTexture(planeObj, fname, 1, gradientTexture)
           
    #Add items from database
    if item == 'employees':
        createButton(stringVal,x,hspace,0.4,0,0.5,4,planeObj)
        hspace = hspace - 2
        cursor.execute("SELECT designation FROM employees WHERE name = ?", (stringVal,) )
        desg = cursor.fetchone()
        cursor.execute("SELECT project FROM employees WHERE name = ?", (stringVal,))
        proj = cursor.fetchall()
        createButton(desg,x,hspace,0.4,0,0.36,3.3,planeObj)
        hspace = hspace - 1
        createButton("PROJECTS",x,hspace,0.4,0,0.4,3.7,planeObj,False,False)
        for p in range(len(proj)):
            hspace = hspace - 1
            createButton(proj[p],x,hspace,0.4,0,0.36,3.3,planeObj,True,False)
                
    elif item == 'projects':
        createNewScene(stringVal, item)
        createButton(stringVal,x,hspace,0.4,0,0.5,4,planeObj,True,True) 
        hspace = hspace -2
        addIconsToProjects(stringVal,planeObj,x,hspace,1)
        hspace = hspace -1
        cursor.execute("SELECT infrastr FROM projects WHERE name = ?", (stringVal,) )
        desg = cursor.fetchone()
        cursor.execute("SELECT method FROM projects WHERE name = ?", (stringVal,))
        proj = cursor.fetchone()

        createButton(desg,x,hspace,0.4,0,0.4,3.7,planeObj)
        hspace = hspace - 1
        createButton(proj,x,hspace,0.4,0,0.4,3.7,planeObj)

        #for p in cursor.execute("SELECT name FROM employees WHERE project = ?", (stringVal,) ):
        #    hspace = hspace - 1
        #    createButton(p,x,hspace,0.4,0,0.4,3.7,planeObj)
            
    elif item == 'methods':
        createButton(stringVal,x,hspace,0.4,0,0.5,4,planeObj)
        hspace = hspace - 2
        addDescriptionTextBox('methods', stringVal, planeObj, 0.3, (x-2), hspace, 0.5)
        #cursor.execute("SELECT description FROM methods WHERE name = ?", (stringVal,) )
        #desg = cursor.fetchone()
        #createButton(desg,x,hspace,0.4,0,0.4,3.7,planeObj)
        
    elif item == 'infrastructure':
        createButton(stringVal,x,hspace,0.4,0,0.5,4,planeObj)
        hspace = hspace - 2
        addDescriptionTextBox('infrastructure', stringVal, planeObj, 0.3, (x-2), hspace, 0.5)
        #cursor.execute("SELECT description FROM infrastructure WHERE name = ?", (stringVal,) )
        #desg = cursor.fetchone()
        #createButton(desg,x,hspace,0.4,0,0.4,3.7,planeObj)
    return planeObj
       
#Create sliding panes for each section(Projects, Employees, Methods, Infrastructure) in the database        
def createSlidingPane(item, x,y,z,dx,dy,dz,xloc,nxloc):
    #Add items from database
    selectStr = "SELECT name from " + item
    cursor.execute(selectStr)
    listofItems = cursor.fetchall()

    handleId = item + 'Handle'
    ePlainObj = createEmptyObject(handleId, 0, 'PLAIN_AXES', xloc,0,0)
        
    for p in range(len(listofItems)):
        stringVal = ''.join(listofItems[p])
        print('Creating Sliding Panes for', stringVal)
        lastPlaneObj = createPanesForItem(item, stringVal,x,0,z,5,dy,dz,3)
        setParent(0, ePlainObj, lastPlaneObj)
        if p == 0:
            backMessage =  item + 'BackMessage'
            slideHandleId = item + 'SlideHandle'

            myButtonProject = Button(item,x,5.3,0.4)
            rightPlaneHeading = myButtonProject.create(0,0.5,4)
            myButtonProject.addMaterialToPlane(greyMaterialObj)
            myButtonProject.addBlinkEffect()
            setParent(1, lastPlaneObj, rightPlaneHeading.planeObj)

            myButtonProject = Button("back",x+15,5.3,0.4)
            rightPlaneBack = myButtonProject.create(0,0.3,2)
            myButtonProject.addMaterialToPlane(greyMaterialObj)
            myButtonProject.addBlinkEffect()
            setParent(1, lastPlaneObj, rightPlaneBack.planeObj)
            addMouseSensor(rightPlaneBack.planeObj.name, 'mleft', 'LEFTCLICK', False)
            addMessageActuator(rightPlaneBack.planeObj.name, 'backMessage',backMessage,slideHandleId)
            addController('LOGIC_AND',rightPlaneBack.planeObj.name,'and3')
            linkSensorAndController(rightPlaneBack.planeObj.name,'mleft','and3')
            linkSensorAndController(rightPlaneBack.planeObj.name,'mo','and3')
            linkActuatorAndController(rightPlaneBack.planeObj.name,'backMessage','and3')
        x = x + 5.4
    addSlideEffect(item, 1, 20, nxloc, ePlainObj)

#Sliding effect for the side panes
def addSlideEffect(item,frameStart,frameEnd,nxloc,ePlainObj):
    backMessage =  item + 'BackMessage'
    attachMessage = 'attachp' + item
    slideMessage = 'slidep' + item 
    slideHandleId = item + 'SlideHandle'
    
    eSphereObj = createEmptyObject(slideHandleId, 0, 'SPHERE', 0,0,0)

    andController = item + 'and'
    addMessageSensor('LeftSidePlane',attachMessage)
    addController('LOGIC_AND','LeftSidePlane',andController)
    addSetParentActuator('LeftSidePlane', attachMessage, slideHandleId)
    addMessageActuator('LeftSidePlane', slideMessage,slideMessage)
    linkSensorAndController('LeftSidePlane',attachMessage,andController)
    linkActuatorAndController('LeftSidePlane',attachMessage,andController)
    linkActuatorAndController('LeftSidePlane',slideMessage,andController)
        
    setParent(0, eSphereObj, ePlainObj)
    actionName = slideHandleId + 'Action'
        
    eSphereObj.location = (0,0,0)
    eSphereObj.keyframe_insert(data_path="location", frame=frameStart)
    eSphereObj.location = (nxloc,0,0)
    eSphereObj.keyframe_insert(data_path="location", frame=frameEnd)
       
    addMessageSensor(slideHandleId,slideMessage);
    addController('LOGIC_AND',slideHandleId,'and1')
    addActionActuator(slideHandleId,'slidingAction',frameStart,frameEnd,actionName)
    linkSensorAndController(slideHandleId,slideMessage,'and1')
    linkActuatorAndController(slideHandleId,'slidingAction','and1')

    addMessageSensor(slideHandleId,backMessage);
    addController('LOGIC_AND',slideHandleId,'and2')    
    addActionActuator(slideHandleId,'backAction',frameEnd,frameStart,actionName)
    linkSensorAndController(slideHandleId,backMessage,'and2')
    linkActuatorAndController(slideHandleId,'backAction','and2')
            
    if item == 'projects':
        selectStr = "SELECT name from " + item
        cursor.execute(selectStr)
        listofItems = cursor.fetchall()
        
        for p in range(len(listofItems)):
            stringVal = ''.join(listofItems[p])
            attachMessage = 'attachDesc' + stringVal
            slideDescMessage = 'slideDesc' + stringVal
            handleId = stringVal + 'PlaneDownHandle'
            andController = 'and' + stringVal
            addMessageSensor(slideHandleId,attachMessage)
            addSetParentActuator(slideHandleId, handleId, handleId)
            addController('LOGIC_AND',slideHandleId,andController)
            linkSensorAndController(slideHandleId,attachMessage,andController)
            linkActuatorAndController(slideHandleId,handleId,andController)
        
            addMessageActuator(slideHandleId, slideDescMessage,slideDescMessage)
            linkActuatorAndController(slideHandleId,slideDescMessage,andController)


######## Create new scenes for each project ############
def createNewScene(name, category):
    planeId = name + 'descPlane'
    fname = homeDir + resourceDir + "Gradient.png"
    planeObj = createSidePane(planeId,0,-3,14,0,12,12,0) #21
    addTexture(planeObj, fname,0,gradientTexture)
    headingButton = Button(name,-3,18,0.4)
    bBack = headingButton.create(0,0.7,5)
    headingButton.addMaterialToPlane(greyMaterialObj)
    headingButton.addBlinkEffect()
    setParent(0,planeObj,bBack.planeObj)

    addTexture(planeObj, fname, 1, gradientTexture)
    addDescriptionTextBox(category, name, planeObj, 0.5, -7, 16, 1)
    addBackButtonForScene(name, planeObj)
    addEmployeeList(name, planeObj)
    addInfrastructureList(name, planeObj)
        
#Add description for project in the new scene
def addDescriptionTextBox(category, name, parentObj, size, xpos, ypos, spacing):
    print('Decription ',name, category)
    cursor.execute("SELECT description FROM {cat} WHERE name = ?" .format(cat=category), (name,) )
    descText = cursor.fetchone()
    #if type(descText) is tuple:
    descText = ''.join(descText)
    subDescText = descText.split("| ")
    pathStr = homeDir + resourceDir + 'Rushmore.otf'
    fnt = bpy.data.fonts.load(pathStr)
    for temp in subDescText:    
        myFontCurve = bpy.data.curves.new(type="FONT",name = "description_text")
        descObj = bpy.data.objects.new(name, myFontCurve)
        descObj.data.body = temp
        descObj.data.size = size
        descObj.data.font = fnt
        descObj.data.text_boxes[0].width = 12
        descObj.data.align_x = 'JUSTIFY'
        descObj.location = (xpos,ypos,0.4)
        ypos = ypos - spacing
        currentScene.objects.link(descObj)
        setParent(0,parentObj,descObj)

#Add employees working on the project as buttons
def addEmployeeList(name, planeObj):
    vspace = -6
    y = 10
    name = (name,)
    for p in cursor.execute("SELECT name FROM employees WHERE project = ?", name ):
        str = ''.join(p)
        myButtonProject = Button(str,vspace,y,0.4)
        vspace = vspace + 3
        bJob = myButtonProject.create(0,0.5,2.8)
        myButtonProject.addMaterialToPlane(greyMaterialObj)
        myButtonProject.addBlinkEffect()
        setParent(0,planeObj,bJob.planeObj)
        
        slideMessage = str + 'moreInfo'
        addMouseSensor(bJob.planeObj.name, 'mleft', 'LEFTCLICK', False)
        addMessageActuator(bJob.planeObj.name, slideMessage,slideMessage)
        addController('LOGIC_AND',bJob.planeObj.name,'and3')
        linkSensorAndController(bJob.planeObj.name,'mleft','and3')
        linkSensorAndController(bJob.planeObj.name,'mo','and3')
        linkActuatorAndController(bJob.planeObj.name,slideMessage,'and3')
        
def addInfrastructureList(name, planeObj):
    cursor.execute("SELECT infrastr FROM projects WHERE name = ?", (name,) )
    desg = cursor.fetchone()
    desg = ''.join(desg)
    planeId = desg + 'sidePlane'
    infrastrPlaneObj = createSidePane(planeId,0,6,17.5,0,5,5,0) #21
    addTexture(infrastrPlaneObj, fname, 1, gradientTexture)
    
    cursor.execute("SELECT method FROM projects WHERE name = ?", (name,))
    method = cursor.fetchone()
    method = ''.join(method)
    planeId = method + 'sidePlane'
    methodPlaneObj = createSidePane(planeId,0,6,10.5,0,5,5,0) #21
    addTexture(methodPlaneObj, fname, 1, gradientTexture)

    createButton(desg,6,18,0.4,0,0.4,3.7,infrastrPlaneObj)
    addDescriptionTextBox('infrastructure', desg, infrastrPlaneObj, 0.3, 4, 17, 0.4)
    createButton(method,6,12,0.4,0,0.4,3.7,methodPlaneObj)
    addDescriptionTextBox('methods', method, methodPlaneObj, 0.3, 4, 11, 0.4)
    setParent(0,planeObj,infrastrPlaneObj)
    setParent(0,planeObj,methodPlaneObj)

#Add backbutton to exit to main menu
def addBackButtonForScene(name, planeObj):
    backButton = Button('BACK',1,17,0.4)
    bBack = backButton.create(0,0.3,2.5)
    backButton.addMaterialToPlane(greyMaterialObj)
    backButton.addBlinkEffect()

    backMessage =  name + 'BackUpMessage'
    #slideHandleId = name + 'Slide
        
    addMouseSensor(bBack.planeObj.name, 'mleft', 'LEFTCLICK', False)
    addMessageActuator(bBack.planeObj.name, 'backUpMessage',backMessage)
    addController('LOGIC_AND',bBack.planeObj.name,'and3')
    linkSensorAndController(bBack.planeObj.name,'mleft','and3')
    linkSensorAndController(bBack.planeObj.name,'mo','and3')
    linkActuatorAndController(bBack.planeObj.name,'backUpMessage','and3')
    setParent(0,planeObj,bBack.planeObj)

def addBackgroundTorus():
    bpy.ops.mesh.primitive_torus_add(view_align=False, location=(0, 0, -8), rotation=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), major_radius=5, minor_radius=2, abso_major_rad=1.25, abso_minor_rad=0.75)
    torusObj = bpy.context.object

    bpy.ops.object.select_all(action='DESELECT') 
    torusObj.select = True
    bpy.data.scenes['Menu'].objects.active = torusObj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.subdivide(number_cuts=2, smoothness=1)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_random(percent=50, seed=0, action='SELECT') 
    bpy.ops.mesh.delete(type='EDGE_FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    filename = homeDir + resourceDir + "8270.jpg"
    addTextureToObject('torusgray',filename,'pinkMetal',torusObj)
    addAlwaysSensor('Torus','always')
    addPythonController('Torus','rpy',"rotate.py")
    #linkSensorAndController('Torus','always','rpy')

def addBackgroundText():
    vlCurve = bpy.data.curves.new(type="FONT",name = "vltext")
    vlCurveObj = bpy.data.objects.new("vlText",vlCurve)
    vlCurveObj.data.body = "VISION LAB"
    vlCurveObj.data.size = 2.5 
    bpy.data.scenes['Menu'].objects.link(vlCurveObj)
    vlCurveObj.select = True
    bpy.data.scenes['Menu'].objects.active = vlCurveObj
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    vlCurveObj.color = (0.8,0.8,0.8,1) 
    vlCurveObj.location = (0,0,-2)

    vlCurveObj.data.extrude = 0.001
    vlCurveObj.data.extrude = 0.2
    vlCurveObj.data.bevel_depth = 0.05
    bpy.ops.object.convert(target='MESH')

    filename = homeDir + resourceDir + "rust.jpg"
    addTextureToObject('vlgray',filename,'rust',vlCurveObj)
        
##############################################################################
#Initial settings
bpy.context.scene.name = 'Menu'
bpy.context.scene.render.engine = 'BLENDER_GAME'
homeDir =  "/home/soja/Desktop/Task1/"
resourceDir = "resources/"
sourceDir = "src/"

currentScene = bpy.data.scenes['Menu']
bpy.ops.object.lamp_add(type='POINT', radius=2, view_align=False, location=(-6, -5, -5), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

addBackgroundTorus()
addBackgroundText()

fname = homeDir + resourceDir + "Gradient.png"
gradientTexture = addMaterialForTexture(fname)

greyMaterialObj = createMaterial("Gray",0.01,0.01,0.5) 

#db_filename = '/home/soja/Desktop/Task1/src/db/visionlab.db'
db_filename = homeDir + sourceDir + 'db/visionlab.db'

lsp = createSidePane('LeftSidePlane',0,-8,0,0,7,13,0)
addTexture(lsp, fname,0,gradientTexture)

conn = sqlite3.connect(db_filename) 
cursor = conn.cursor()

hspace = 2
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    str = ''.join(row)
    if str != 'sqlite_sequence':
        myButtonProject = Button(str,-8,hspace,0.4)
        hspace = hspace - 1
        bP = myButtonProject.create(0,0.6,6)
        myButtonProject.addMaterialToPlane(greyMaterialObj)
        myButtonProject.addBlinkEffect()
        setParent(0,lsp,bP.planeObj)
        addMouseSensor(bP.planeObj.name, 'mleft', 'LEFTCLICK', False)
        addMessageActuator(bP.planeObj.name, 'slideMessage','attach'+ bP.planeObj.name)
        addController('LOGIC_AND',bP.planeObj.name,'and3')
        linkSensorAndController(bP.planeObj.name,'mleft','and3')
        linkSensorAndController(bP.planeObj.name,'mo','and3')
        linkActuatorAndController(bP.planeObj.name,'slideMessage','and3')

bpy.context.screen.scene = bpy.data.scenes['Menu']
itemName = 'projects'
createSlidingPane(itemName,17,0,0,7,13,0,16,-24);
itemName = 'methods'
createSlidingPane(itemName,17,0,0,7,13,0,16,-24);
itemName = 'infrastructure'
createSlidingPane(itemName,17,0,0,7,13,0,16,-24);
itemName = 'employees'
createSlidingPane(itemName,17,0,0,7,13,0,16,-24);
