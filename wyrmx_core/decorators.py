from typing import Any
from fastapi import APIRouter

from wyrmx_core.scope import Scope
from wyrmx_core.container import container
from wyrmx_core.router import registerRouter

def singleton(cls):
    """
    Decorator to mark a class as a singleton.
    """

    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def controller(routerPrefix: str, scope: Scope = Scope.SINGLETON):
    """
    Decorator to mark a class as a controller with a base route.
    Also enforces singleton.
    """

    def bindEndpoints(instance: Any):

         for attr_name in dir(instance):
            attr = getattr(instance, attr_name)

            if callable(attr) and hasattr(attr, "_route_info"):
                instance.router.add_api_route(
                    attr._route_info["path"],
                    attr,
                    methods=attr._route_info["methods"]
                )


    def decorator(cls):
        setattr(cls, "isController", True)
        setattr(cls, "routerPrefix", routerPrefix)
        setattr(cls, "router", APIRouter(prefix=f"/{routerPrefix}"))

        
        container.register(cls, scope)
        instance = container.resolve(cls)
        
        bindEndpoints(instance)
        registerRouter(instance.router)

        

        return cls
    
    return decorator


def service(cls, scope: Scope = Scope.SINGLETON):
    """
    Decorator to mark a class as a service with a base route.
    Also enforces singleton.
    """

    setattr(cls, "isService", True)
    container.register(cls, scope)

    return cls

def model(cls):
    setattr(cls, "isModel", True)
    return cls


def schema(cls):
    setattr(cls, "isSchema", True)
    return cls



