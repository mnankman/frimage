import lib.wxdyn.log as  log
from lib.wxdyn import util
from .pubsub import Publisher
from .persistentobject import PersistentObject

class ModelObject(PersistentObject, Publisher):
    EVENTS = ["msg_object_modified", "msg_new_child"]
    """
    This is the base class for all the other model classes. It implements the object 
    hierarchy and the model modification status. 
    extends PersistentObject to enable instance of ModelObject to serialize/deserialize their internal state
    extends Publisher to allow Subscriber instances to be notified about the modification state.  
    """
    __lastId__ = 0
    def nextId():
        id = ModelObject.__lastId__
        ModelObject.__lastId__ += 1
        return id

    def __init__(self, parent=None):
        PersistentObject.__init__(self)
        Publisher.__init__(self, ModelObject.EVENTS)
        self.__modified__ = False
        self.__children__ = {}
        self.__parent__ = None
        self.__objectId__ = ModelObject.nextId()
        if parent:
            assert isinstance(parent, ModelObject)
            self.__parent__ = parent
            parent.addChild(self)

    def __del__(self):
        log.trace(function=self.__del__, args=self.getFullId())
        self.destroy()

    def destroy(self):
        Publisher.__destroy__(self)
        parent = self.getParent()
        if parent:
            parent.removeChild(self)
        self._reset()

    def _reset(self):
        for c in self.getChildren():
            del c
        self.__modified__ = False
        self.__children__ = {}

    def setModified(self):
        if not self.__modified__:
            log.trace(self.getFullId()+".setModified()")
            self.__modified__ = True
            self.dispatch("msg_object_modified", {"object": self} )

    def clearModified(self, recursive=False):
        self.__modified__ = False
        if recursive:
            for c in self.getChildren():
                c.clearModified(recursive)
        log.debug(function=self.clearModified, args=recursive, var=("self.__modified__", self.__modified__))

    def getParent(self):
        return self.__parent__

    def setParent(self, parent):
        assert isinstance(parent, ModelObject)
        self.__parent__.removeChild(self)
        self.__parent__ = parent
        parent.addChild(self)
    
    def isValidChild(self, child):
        valid = False
        if child and isinstance(child, ModelObject):
            valid = child in self.__children__.values() and child.getParent() == self
        return valid

    def getFullId(self):
        result = self.getId()
        p = self.getParent()
        if p!=None and isinstance(p, ModelObject):
            result = p.getFullId() + "/" + result
        return result

    def getId(self):
        return self.getType() + str(self.__objectId__)

    def getChildren(self):
        if not self.__children__: self.__children = []
        return self.__children__.values()

    def addChild(self, childObject):
        log.debug(function=self.addChild, args=childObject.getFullId())
        assert isinstance(childObject, ModelObject)
        self.__children__[childObject.getId()] = childObject
        assert self.isValidChild(childObject) == True
        self.dispatch("msg_new_child", {"object": self, "child": childObject})
        childObject.subscribe(self, "msg_object_modified", self.onMsgChildObjectModified)
        self.setModified()

    def removeChild(self, childObject):
        log.debug(function=self.removeChild, args=childObject.getFullId())
        assert isinstance(childObject, ModelObject)
        if childObject.getId() in self.getChildren():
            self.__children__.pop(childObject.getId())
            childObject.unsubscribe(self.onMsgChildObjectModified, "msg_object_modified")
            self.setModified()

    def onMsgChildObjectModified(self, payload):
        log.debug(function=self.onMsgChildObjectModified, args=payload["object"].getFullId())
        self.dispatch("msg_object_modified", {"object": self, "modified": payload})

    def getModificationsFromPayload(self, payload):
        modifications = []
        if "object" in payload:
            obj = payload["object"]
            modifications.append(obj.getFullId())
        if "modified" in payload:
            modifications.extend(self.getModificationsFromPayload(payload["modified"]))
        return modifications

    def getModified(self, recursive=True):
        if not self.__modified__ and recursive:
            return self.getChildModified(recursive)
        else:
            return self.__modified__

    def isModified(self, recursive=False):
        return self.getModified(recursive)

    def getChildModified(self, recursive=False):
        for c in self.getChildren():
            if recursive:
                return c.getModified(recursive)
        return False

    def getModifiedObjects(self):
        modified = []
        if self.__modified__:
            modified.append(self)
        for c in self.getChildren():
            modified = modified + c.getModifiedObjects()
        return modified

    def serialize(self):
        data = PersistentObject.serialize(self)
        for c in self.getChildren():
            childdata = c.serialize()
            data = self.addNestedElement(data, childdata)
        return data

    def setAttribute(self, attr, attrValue):
        super().setDataAttribute(attr, attrValue)

    def getAttribute(self, attr):
        getterName = "get"+util.upperFirst(attr)
        assert hasattr(type(self), getterName)
        get = getattr(type(self), getterName)
        log.debug(function=self.getAttribute, args=attr)
        log.debug(function=get)
        return get(self)

    def hasAttribute(self, attr):
        getterName = "get"+util.upperFirst(attr)
        return hasattr(type(self), getterName)
        
