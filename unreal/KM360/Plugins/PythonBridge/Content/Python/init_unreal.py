import unreal

try:
    import python_bridge

    if python_bridge.REGISTRATION.register():
        unreal.log("PythonBridge: PythonBridgeToolset registered.")
    else:
        unreal.log_warning("PythonBridge: Toolset Registry not available, PythonBridgeToolset not registered.")
except Exception as e:  # never break editor startup
    unreal.log_error(f"PythonBridge: failed to register toolset: {e}")
