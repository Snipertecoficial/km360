#!/usr/bin/env python3
"""Cliente mínimo do Unreal MCP (Streamable HTTP em 127.0.0.1:8000/mcp). Só stdlib.

Uso:
  python3 mcp.py tools                         # meta-ferramentas expostas
  python3 mcp.py toolsets                      # list_toolsets
  python3 mcp.py describe <toolset>            # describe_toolset
  python3 mcp.py call <toolset> <tool> '<json>'# call_tool
  python3 mcp.py py '<código python>'          # PythonBridge run_python
  python3 mcp.py pyfile <caminho.py>           # PythonBridge run_python_file
"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("UNREAL_MCP_URL", "http://127.0.0.1:8000/mcp")
BRIDGE = "python_bridge.toolset.PythonBridgeToolset"
_session = {"id": None, "n": 0}


def _post(method, params=None, notify=False):
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not notify:
        _session["n"] += 1
        body["id"] = _session["n"]
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if _session["id"]:
        headers["Mcp-Session-Id"] = _session["id"]
    req = urllib.request.Request(URL, json.dumps(body).encode(), headers)
    with urllib.request.urlopen(req, timeout=float(os.environ.get("UNREAL_MCP_TIMEOUT", "900"))) as r:
        _session["id"] = r.headers.get("Mcp-Session-Id") or _session["id"]
        raw = r.read().decode("utf-8", "replace")
        ctype = r.headers.get("Content-Type", "")
    if notify or not raw.strip():
        return None
    if "text/event-stream" in ctype:  # pega o último evento com resposta
        msgs = [json.loads(l[5:]) for l in raw.splitlines() if l.startswith("data:") and l[5:].strip()]
        msg = next((m for m in reversed(msgs) if "result" in m or "error" in m), msgs[-1] if msgs else {})
    else:
        msg = json.loads(raw)
    if "error" in msg:
        raise SystemExit(f"MCP error: {json.dumps(msg['error'], ensure_ascii=False)}")
    return msg.get("result")


def connect():
    _post("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                         "clientInfo": {"name": "km360-cli", "version": "0.1"}})
    _post("notifications/initialized", notify=True)


def tool(name, args):
    res = _post("tools/call", {"name": name, "arguments": args}) or {}
    text = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
    if res.get("isError"):
        raise SystemExit(f"TOOL ERROR:\n{text}")
    try:  # PythonBridge devolve {"returnValue": "..."}: mostra só o texto
        value = json.loads(text)["returnValue"]
        if isinstance(value, str):
            return value
    except (ValueError, KeyError, TypeError):
        pass
    return text or json.dumps(res.get("structuredContent", res), ensure_ascii=False, indent=1)


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    connect()
    cmd, rest = argv[0], argv[1:]
    if cmd == "tools":
        print("\n".join(t["name"] for t in (_post("tools/list") or {}).get("tools", [])))
    elif cmd == "toolsets":
        print(tool("list_toolsets", {}))
    elif cmd == "describe":
        print(tool("describe_toolset", {"toolset_name": rest[0]}))
    elif cmd == "call":
        print(tool("call_tool", {"toolset_name": rest[0], "tool_name": rest[1],
                                 "arguments": json.loads(rest[2]) if len(rest) > 2 else {}}))
    elif cmd == "py":
        print(tool("call_tool", {"toolset_name": BRIDGE, "tool_name": "run_python", "arguments": {"code": rest[0]}}))
    elif cmd == "pyfile":
        print(tool("call_tool", {"toolset_name": BRIDGE, "tool_name": "run_python_file",
                                 "arguments": {"file_path": os.path.abspath(rest[0])}}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
