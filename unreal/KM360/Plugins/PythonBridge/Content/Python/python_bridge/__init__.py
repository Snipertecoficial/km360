from toolset_registry.registration import Registration

from .toolset import PythonBridgeToolset

REGISTRATION = Registration([PythonBridgeToolset])
