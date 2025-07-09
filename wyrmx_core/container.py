from wyrmx_core.scope import Scope

import inspect


class Container: 

    def __init__(self):
        self.__providers = {}
        self.__instances = {}
    

    def register(self, cls, scope: Scope = Scope.SINGLETON):
        self.__providers[cls] = (cls, scope)
    
    def resolve(self, cls):
        
        provider, scope = self.__providers[cls]

        if scope == Scope.SINGLETON and cls in self.__instances: return self.__instances[cls]

        ctor = inspect.signature(provider.__init__)
        deps = [self.resolve(p.annotation) for n, p in list(ctor.parameters.items())[1:]]
        instance = provider(*deps)

        if scope == Scope.SINGLETON: self.__instances[cls] = instance

        return instance


container = Container()