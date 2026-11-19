"""Python Bridge: run Python in the real editor interpreter through Unreal MCP."""

import ast
import contextlib
import io
import os
import traceback

import toolset_registry
import unreal

_MAX_CHARS = 6000
_HEAD_TAIL = 2500
_state = {"globals": None, "n": 0}


def _project_dir() -> str:
    return os.path.abspath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))


def _namespace(reset: bool) -> dict:
    if reset or _state["globals"] is None:
        _state["globals"] = {"__name__": "__python_bridge__", "unreal": unreal}
    return _state["globals"]


def _cap(text: str) -> str:
    """Long output goes to Saved/PythonBridge/output_NNN.txt; returns head, tail and path."""
    if len(text) <= _MAX_CHARS:
        return text
    folder = os.path.join(_project_dir(), "Saved", "PythonBridge")
    os.makedirs(folder, exist_ok=True)
    _state["n"] += 1
    path = os.path.join(folder, f"output_{_state['n']:03d}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return f"{text[:_HEAD_TAIL]}\n...[{len(text)} chars, full output in {path}]...\n{text[-_HEAD_TAIL:]}"


def _run(code: str, reset: bool, filename: str) -> str:
    ns = _namespace(reset)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            tree = ast.parse(code, filename, "exec")
            tail = None
            if tree.body and isinstance(tree.body[-1], ast.Expr):  # REPL: last expression is echoed
                tail = ast.Expression(tree.body.pop().value)
            exec(compile(tree, filename, "exec"), ns)
            if tail is not None:
                value = eval(compile(tail, filename, "eval"), ns)
                if value is not None:
                    print(repr(value))
    except Exception as e:
        te = traceback.TracebackException.from_exception(e)
        te.stack = traceback.StackSummary.from_list([fr for fr in te.stack if fr.filename != __file__])
        raise RuntimeError(_cap(out.getvalue() + "".join(te.format()))) from None
    return _cap(out.getvalue())


@unreal.uclass()
class PythonBridgeToolset(unreal.ToolsetDefinition):
    """Runs Python in the Unreal Editor's own interpreter with the full `import unreal` API.

    Prefer a typed toolset when one does the job. Use this for what they can't do
    (editor scripting, Sequencer, Movie Render Queue, Geometry Script, measuring assets).
    Through call_tool use the short tool name (run_python) plus the full toolset name
    python_bridge.toolset.PythonBridgeToolset. Call get_environment_info once first.
    """

    @toolset_registry.tool_call
    @staticmethod
    def get_environment_info() -> str:
        """Explains how this toolset behaves. Call it once before the first run_python.

        Returns:
            Rules, engine version and project folder.
        """
        return "\n".join([
            f"Engine: {unreal.SystemLibrary.get_engine_version()}",
            f"Project folder: {_project_dir()}",
            "Code runs in the editor's Python interpreter on the game thread; `unreal` is preloaded.",
            "Globals persist between calls in one shared namespace; reset_globals=True starts clean.",
            "stdout and stderr are captured and returned; a final expression is echoed like a REPL.",
            f"Output over {_MAX_CHARS} chars is saved to Saved/PythonBridge/output_NNN.txt (head, tail and path are returned).",
            "Errors raise with the traceback of your own code plus anything printed before the failure.",
            "Print narrowly: return counts and names, not whole object dumps.",
            "NEVER call time.sleep(): it blocks the game thread and freezes the editor.",
            "To watch something over time use unreal.register_slate_post_tick_callback and read the result in a later call.",
            "Wrap scene changes in unreal.ScopedEditorTransaction so a single Ctrl+Z undoes them.",
        ])

    @toolset_registry.tool_call
    @staticmethod
    def run_python(code: str, reset_globals: bool = False) -> str:
        """Runs a short Python snippet in the editor and returns what it printed.

        Args:
            code: Python source. `unreal` is already imported. Keep it under about 20 lines;
                use run_python_file for longer scripts.
            reset_globals: Start from a clean namespace instead of reusing earlier variables.

        Returns:
            Captured stdout/stderr, plus the repr of a final expression if there is one.
        """
        return _run(code, reset_globals, "<run_python>")

    @toolset_registry.tool_call
    @staticmethod
    def run_python_file(file_path: str, reset_globals: bool = False) -> str:
        """Runs a Python file in the editor and returns what it printed.

        Args:
            file_path: Absolute path, or relative to the project folder. Preferred for
                anything longer than about 20 lines.
            reset_globals: Start from a clean namespace instead of reusing earlier variables.

        Returns:
            Captured stdout/stderr, plus the repr of a final expression if there is one.
        """
        path = file_path if os.path.isabs(file_path) else os.path.join(_project_dir(), file_path)
        with open(path, encoding="utf-8") as f:
            return _run(f.read(), reset_globals, path)
