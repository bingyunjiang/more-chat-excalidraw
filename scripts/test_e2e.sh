#!/usr/bin/env bash
# End-to-end test for more-chat-excalidraw
# Usage: bash scripts/test_e2e.sh [--sandbox]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SANDBOX="${1:-}"

pass=0
fail=0
warn=0

log_pass() { echo "[PASS] $1"; pass=$((pass+1)); }
log_fail() { echo "[FAIL] $1"; fail=$((fail+1)); }
log_warn() { echo "[WARN] $1"; warn=$((warn+1)); }

# --- Test 1: Validate fixture ---
echo "=== Test 1: Validate fixture ==="
if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" "$PROJECT_DIR/output/fixture-flowchart.excalidraw"; then
  log_pass "validate fixture-flowchart.excalidraw"
else
  log_fail "validate fixture-flowchart.excalidraw"
fi

# --- Test 2: Validate minimal file ---
echo "=== Test 2: Validate minimal file ==="
MINIMAL="/tmp/test-minimal.excalidraw"
# Always rebuild: CI environments have no stale /tmp file. Two elements
# (rectangle + text) keep the later "push_preview updates scene" check at total:2.
cat > "$MINIMAL" << 'MINEOF'
{"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":[
  {"id":"r1","type":"rectangle","x":0,"y":0,"width":100,"height":60,"strokeColor":"#1e1e1e","backgroundColor":"#ffffff","fillStyle":"solid","strokeWidth":1,"roughness":0,"opacity":100,"angle":0,"seed":1,"groupIds":[],"boundElements":[],"updated":1,"link":null,"locked":false},
  {"id":"t1","type":"text","x":10,"y":20,"width":80,"height":20,"text":"hello","fontSize":14,"fontFamily":1,"textAlign":"left","verticalAlign":"top","containerId":null,"originalText":"hello","lineHeight":1.25,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":1,"roughness":0,"opacity":100,"angle":0,"seed":2,"groupIds":[],"boundElements":[],"updated":1,"link":null,"locked":false}
],"appState":{"viewBackgroundColor":"#ffffff"}}
MINEOF
if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" "$MINIMAL"; then
  log_pass "validate minimal file"
else
  log_fail "validate minimal file"
fi

# --- Test 3: Validate rejects bad file ---
echo "=== Test 3: Validate rejects bad file ==="
BAD_FILE="/tmp/test-bad.excalidraw"
echo '{"type":"wrong","version":1}' > "$BAD_FILE"
if ! python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" "$BAD_FILE" >/dev/null 2>&1; then
  log_pass "validate correctly rejects bad file"
else
  log_fail "validate should reject bad file"
fi

# --- Test 4: Render ---
echo "=== Test 4: Render ==="
RENDER_OUT="/tmp/e2e-render-test"
rm -rf "$RENDER_OUT"
mkdir -p "$RENDER_OUT"

if [ "$SANDBOX" = "--sandbox" ]; then
  echo "Running in sandbox mode (expecting fallback SVG)..."
  if node "$PROJECT_DIR/scripts/render_preview.js" "$MINIMAL" "$RENDER_OUT" --format svg --no-server 2>&1; then
    if [ -f "$RENDER_OUT/test-minimal.svg" ]; then
      log_pass "render fallback SVG in sandbox"
    else
      log_fail "render fallback SVG: file not created"
    fi
  else
    log_fail "render fallback SVG"
  fi
else
  echo "Running with full privileges (expecting Playwright render)..."
  if node "$PROJECT_DIR/scripts/render_preview.js" "$MINIMAL" "$RENDER_OUT" --format both 2>&1; then
    if [ -f "$RENDER_OUT/test-minimal.png" ] && [ -f "$RENDER_OUT/test-minimal.svg" ]; then
      log_pass "render PNG + SVG with Playwright"
      if python3 - "$RENDER_OUT/test-minimal.png" <<'PY'
import struct, sys
with open(sys.argv[1], "rb") as fh:
    header = fh.read(24)
if header[:8] != b"\x89PNG\r\n\x1a\n":
    raise SystemExit("not a PNG")
width, height = struct.unpack(">II", header[16:24])
if width >= 1000 or height >= 1000:
    raise SystemExit(f"export contains page chrome/whitespace: {width}x{height}")
PY
      then
        log_pass "PNG export is cropped to diagram bounds"
      else
        log_fail "PNG export includes verification page chrome or whitespace"
      fi
    else
      log_warn "render completed but missing output files"
    fi
  else
    log_fail "render with Playwright"
  fi
fi

# --- Test 5: Open --check-only ---
echo "=== Test 5: Service check ==="
if node "$PROJECT_DIR/scripts/open_in_excalidraw.js" --check-only 2>&1; then
  log_pass "Excalidraw service is reachable"
else
  log_warn "Excalidraw service not reachable (may need --start)"
fi

# --- Test 6: Preview server (real-time polling API) ---
echo "=== Test 6: Preview server ==="
PREVIEW_PORT="${PREVIEW_TEST_PORT:-6099}"
PREVIEW_LOG="/tmp/e2e-preview-server.log"
rm -f "$PREVIEW_LOG"

node "$PROJECT_DIR/scripts/preview_server.js" --port "$PREVIEW_PORT" \
  "$PROJECT_DIR/output/fixture-flowchart.excalidraw" > "$PREVIEW_LOG" 2>&1 &
PREVIEW_PID=$!

# Wait for server to come up
SERVER_UP=0
for i in $(seq 1 20); do
  if curl -s -o /dev/null "http://localhost:${PREVIEW_PORT}/api/status"; then
    SERVER_UP=1
    break
  fi
  sleep 0.5
done

if [ "$SERVER_UP" = "1" ]; then
  log_pass "preview server started on port $PREVIEW_PORT"

  # 6a: GET /api/status has element counts
  STATUS_JSON=$(curl -s "http://localhost:${PREVIEW_PORT}/api/status")
  if echo "$STATUS_JSON" | grep -q '"total":14'; then
    log_pass "preview server loaded fixture (14 elements)"
  else
    log_fail "preview server fixture load (got: $STATUS_JSON)"
  fi

  # 6b: GET /api/diagram.svg returns SVG with arrows and texts
  SVG_OUT=$(curl -s "http://localhost:${PREVIEW_PORT}/api/diagram.svg")
  if echo "$SVG_OUT" | grep -q "<svg" && echo "$SVG_OUT" | grep -q "<path"; then
    log_pass "preview server renders SVG with paths"
  else
    log_fail "preview server SVG render"
  fi

  # 6c: POST a different diagram, verify it replaces the scene
  if node "$PROJECT_DIR/scripts/push_preview.js" "$MINIMAL" --url "http://localhost:${PREVIEW_PORT}" >/dev/null 2>&1; then
    sleep 0.3
    STATUS_JSON2=$(curl -s "http://localhost:${PREVIEW_PORT}/api/status")
    if echo "$STATUS_JSON2" | grep -q '"total":2'; then
      log_pass "push_preview.js updates the scene in real time (2 elements)"
    else
      log_fail "push_preview.js update (got: $STATUS_JSON2)"
    fi
  else
    log_fail "push_preview.js"
  fi

  # 6d: GET / serves the preview page
  PAGE_OUT=$(curl -s "http://localhost:${PREVIEW_PORT}/")
  if echo "$PAGE_OUT" | grep -q "实时预览"; then
    log_pass "preview page served"
  else
    log_fail "preview page"
  fi

  # 6e: GET /editor serves the embedded Excalidraw editor page
  EDITOR_OUT=$(curl -s "http://localhost:${PREVIEW_PORT}/editor")
  if echo "$EDITOR_OUT" | grep -q "editor-bundle.js" && echo "$EDITOR_OUT" | grep -q "editor-mount"; then
    log_pass "editor page served with bundle script"
  else
    log_fail "editor page"
  fi

  # 6f: GET /editor-bundle.js serves the bundled Excalidraw editor
  BUNDLE_TMP="/tmp/e2e-editor-bundle.js"
  curl -s "http://localhost:${PREVIEW_PORT}/editor-bundle.js" -o "$BUNDLE_TMP"
  if grep -q "ExcalidrawEditorBundle" "$BUNDLE_TMP" && [ -s "$PROJECT_DIR/scripts/web/editor-bundle.js" ]; then
    log_pass "editor bundle served"
  else
    log_fail "editor bundle missing or invalid (run: npm run build:all --prefix scripts/web)"
  fi

  # 6g: GET /excalidraw-css serves the Excalidraw stylesheet
  CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PREVIEW_PORT}/excalidraw-css")
  if [ "$CSS_STATUS" = "200" ]; then
    log_pass "excalidraw css served (HTTP 200)"
  else
    log_warn "excalidraw css (HTTP $CSS_STATUS)"
  fi

  # 6h: POST /api/save persists the scene (write-through to scene file)
  SAVE_PORT=$((PREVIEW_PORT + 1))
  SAVE_FILE="/tmp/e2e-save-scene.excalidraw"
  echo '{"type":"excalidraw","version":2,"elements":[{"id":"base1","type":"rectangle","x":0,"y":0,"width":100,"height":50,"angle":0,"strokeColor":"#000","backgroundColor":"#fff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":1,"version":1,"versionNonce":0,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false}],"appState":{}}' > "$SAVE_FILE"
  node "$PROJECT_DIR/scripts/preview_server.js" --port "$SAVE_PORT" "$SAVE_FILE" > /tmp/e2e-save-server.log 2>&1 &
  SAVE_PID=$!
  for i in $(seq 1 20); do
    if curl -s -o /dev/null "http://localhost:${SAVE_PORT}/api/status"; then
      break
    fi
    sleep 0.5
  done
  SAVE_BODY='{"elements":[{"id":"s1","type":"rectangle","x":0,"y":0,"width":100,"height":50,"angle":0,"strokeColor":"#000","backgroundColor":"#fff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":1,"version":1,"versionNonce":0,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false}],"appState":{}}'
  SAVE_RESULT=$(curl -s -X POST "http://localhost:${SAVE_PORT}/api/save" -H "Content-Type: application/json" -d "$SAVE_BODY")
  if echo "$SAVE_RESULT" | grep -q '"success":true' && grep -q '"s1"' "$SAVE_FILE"; then
    log_pass "/api/save persisted write-through to scene file"
  else
    log_fail "/api/save (got: $SAVE_RESULT)"
  fi
  kill "$SAVE_PID" 2>/dev/null
  wait "$SAVE_PID" 2>/dev/null

  # 6i: POST /api/canvases creates a named canvas
  CANVAS_BODY='{"name":"e2e-canvas","elements":[{"id":"c1","type":"rectangle","x":0,"y":0,"width":100,"height":50,"angle":0,"strokeColor":"#000","backgroundColor":"#fff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":1,"version":1,"versionNonce":0,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false}],"appState":{}}'
  CANVAS_RESULT=$(curl -s -X POST "http://localhost:${PREVIEW_PORT}/api/canvases" -H "Content-Type: application/json" -d "$CANVAS_BODY")
  if echo "$CANVAS_RESULT" | grep -q '"e2e-canvas"'; then
    log_pass "/api/canvases created named canvas"
  else
    log_fail "/api/canvases create (got: $CANVAS_RESULT)"
  fi

  # 6j: GET /api/canvases lists canvases
  CANVAS_LIST=$(curl -s "http://localhost:${PREVIEW_PORT}/api/canvases")
  if echo "$CANVAS_LIST" | grep -q '"e2e-canvas"'; then
    log_pass "/api/canvases lists canvases"
  else
    log_fail "/api/canvases list (got: $CANVAS_LIST)"
  fi

  # 6k: GET /animate serves the animation playback page
  ANIM_PAGE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PREVIEW_PORT}/animate")
  if [ "$ANIM_PAGE" = "200" ]; then
    log_pass "animation page served (HTTP 200)"
  else
    log_fail "animation page (HTTP $ANIM_PAGE)"
  fi

  # 6l: GET /api/animate returns frame sequence
  ANIM_JSON=$(curl -s "http://localhost:${PREVIEW_PORT}/api/animate")
  if echo "$ANIM_JSON" | grep -q '"total":'; then
    log_pass "/api/animate returns frame sequence"
  else
    log_fail "/api/animate (got: $ANIM_JSON)"
  fi
else
  log_fail "preview server failed to start"
  cat "$PREVIEW_LOG" 2>/dev/null | tail -5
fi

kill "$PREVIEW_PID" 2>/dev/null
wait "$PREVIEW_PID" 2>/dev/null
echo "--- preview server log ---"
cat "$PREVIEW_LOG" 2>/dev/null | tail -3

# --- Test 7: Mermaid -> Excalidraw conversion (C.6) ---
echo "=== Test 7: Mermaid conversion ==="
MMD_INLINE='graph TD; A[开始] --> B[处理]; B --> C{成功?}; C -->|是| D[完成]'
if node "$PROJECT_DIR/scripts/mermaid_to_excalidraw.js" --string "$MMD_INLINE" --output /tmp/e2e-mermaid.excalidraw >/dev/null 2>&1; then
  if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-mermaid.excalidraw >/dev/null 2>&1; then
    log_pass "mermaid flowchart converts to valid excalidraw"
  else
    log_fail "mermaid output failed validation"
  fi
else
  log_fail "mermaid_to_excalidraw.js"
fi

MMD_SEQ='sequenceDiagram; participant 用户; participant 服务端; 用户->>服务端: 请求'
if node "$PROJECT_DIR/scripts/mermaid_to_excalidraw.js" --string "$MMD_SEQ" --output /tmp/e2e-mermaid-seq.excalidraw >/dev/null 2>&1; then
  log_pass "mermaid sequence converts to excalidraw"
else
  log_fail "mermaid sequence conversion"
fi

# --- Test 8: Knowledge graph -> architecture (C.8) ---
echo "=== Test 8: Knowledge graph generation ==="
KG_TEXT="/tmp/e2e-kg.txt"
cat > "$KG_TEXT" << 'KGEOF'
entity: Web前端|component|用户层
entity: 订单服务|service|应用层
entity: PostgreSQL|database|数据层
rel: Web前端 -> 订单服务 调用
rel: 订单服务 -> PostgreSQL 读写
KGEOF
if python3 "$PROJECT_DIR/scripts/knowledge_graph.py" --text "$KG_TEXT" --output /tmp/e2e-kg.excalidraw >/dev/null 2>&1; then
  if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-kg.excalidraw >/dev/null 2>&1; then
    log_pass "knowledge graph generates valid architecture excalidraw"
  else
    log_fail "knowledge graph output failed validation"
  fi
else
  log_fail "knowledge_graph.py"
fi

# --- Test 9: Graphviz layout (C.2) ---
echo "=== Test 9: Graphviz layout ==="
if command -v dot >/dev/null 2>&1; then
  if python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example architecture --layout dot --output /tmp/e2e-graphviz.excalidraw >/dev/null 2>&1; then
    if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-graphviz.excalidraw >/dev/null 2>&1; then
      log_pass "graphviz dot layout generates valid excalidraw"
    else
      log_fail "graphviz output failed validation"
    fi
  else
    log_fail "ir_to_excalidraw --layout dot"
  fi
else
  log_warn "graphviz not installed; skipping layout test (brew install graphviz)"
fi

# --- Test 10: Incremental merge (C.5) ---
echo "=== Test 10: Incremental merge ==="
if python3 "$PROJECT_DIR/scripts/merge_excalidraw.py" patch /tmp/e2e-kg.excalidraw --set 'n2.backgroundColor=#ffc9c9' --history-dir /tmp/e2e-merge-history >/dev/null 2>&1; then
  if grep -q "#ffc9c9" /tmp/e2e-kg.excalidraw; then
    log_pass "merge patch updates element color"
  else
    log_fail "merge patch color not applied"
  fi
else
  log_fail "merge_excalidraw.py patch"
fi

# --- Test 11: MCP server (D.6) ---
echo "=== Test 11: MCP server ==="
if [ -f "$PROJECT_DIR/scripts/web/node_modules/@modelcontextprotocol/sdk/dist/esm/server/mcp.js" ] && [ -d "$PROJECT_DIR/scripts/web/node_modules/zod" ]; then
  cat > /tmp/e2e-mcp-req.jsonl << 'MCPEOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"e2e","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"generate_diagram","arguments":{"ir":{"version":1,"title":"mcp-e2e","template":"flowchart","nodes":[{"id":"a","label":"A","type":"start"},{"id":"b","label":"B","type":"end"}],"edges":[{"id":"e","from":"a","to":"b"}]},"output":"/tmp/e2e-mcp-generated.excalidraw"}}}
MCPEOF
  node "$PROJECT_DIR/scripts/mcp_server.mjs" < /tmp/e2e-mcp-req.jsonl > /tmp/e2e-mcp-out.log 2>/dev/null &
  MCP_PID=$!
  sleep 4
  kill "$MCP_PID" 2>/dev/null
  MCP_OUT=$(cat /tmp/e2e-mcp-out.log)
  if echo "$MCP_OUT" | grep -q '"generate_diagram"' && echo "$MCP_OUT" | grep -q '"list_templates"' && [ -s /tmp/e2e-mcp-generated.excalidraw ]; then
    log_pass "MCP server registers tools and executes generate_diagram"
  else
    log_fail "MCP server tool registration"
  fi
else
  log_fail "MCP SDK/zod missing after npm ci"
fi

# --- Test 11b: deterministic generation + library path ---
echo "=== Test 11b: Deterministic/library generation ==="
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example flowchart --output /tmp/e2e-det-a.excalidraw >/dev/null 2>&1 && \
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example flowchart --output /tmp/e2e-det-b.excalidraw >/dev/null 2>&1 && \
cmp -s /tmp/e2e-det-a.excalidraw /tmp/e2e-det-b.excalidraw
if [ "$?" -eq 0 ]; then log_pass "same IR produces byte-identical output"; else log_fail "generation is not deterministic"; fi
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example fea --output /tmp/e2e-fea-a.excalidraw >/dev/null 2>&1 && \
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example fea --output /tmp/e2e-fea-b.excalidraw >/dev/null 2>&1 && \
cmp -s /tmp/e2e-fea-a.excalidraw /tmp/e2e-fea-b.excalidraw && \
python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-fea-a.excalidraw --visual --fail-on-warning >/dev/null 2>&1
if [ "$?" -eq 0 ]; then log_pass "FEA swimlane is deterministic and strict-visual clean"; else log_fail "FEA swimlane regression"; fi
if python3 - /tmp/e2e-fea-a.excalidraw <<'PY'
import json, sys
scene = json.load(open(sys.argv[1], encoding="utf-8"))
frames = [el for el in scene.get("elements", []) if el.get("type") == "frame"]
if len(frames) != 4:
    raise SystemExit(f"expected 4 FEA stage frames, got {len(frames)}")
xs = [el["x"] for el in frames]
ys = [el["y"] for el in frames]
x2 = [el["x"] + el.get("width", 0) for el in frames]
y2 = [el["y"] + el.get("height", 0) for el in frames]
width, height = max(x2) - min(xs), max(y2) - min(ys)
if width / max(height, 1) < 1.8:
    raise SystemExit(f"FEA layout regressed to a tall diagram: {width}x{height}")
PY
then log_pass "FEA uses four-stage landscape engineering layout"; else log_fail "FEA engineering layout/aspect ratio"; fi
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example battery-thermal --output /tmp/e2e-battery-a.excalidraw >/dev/null 2>&1 && \
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example battery-thermal --output /tmp/e2e-battery-b.excalidraw >/dev/null 2>&1 && \
cmp -s /tmp/e2e-battery-a.excalidraw /tmp/e2e-battery-b.excalidraw && \
python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-battery-a.excalidraw --visual --fail-on-warning >/dev/null 2>&1
if [ "$?" -eq 0 ]; then log_pass "battery thermal architecture is deterministic and strict-visual clean"; else log_fail "battery thermal architecture regression"; fi
if python3 - /tmp/e2e-battery-a.excalidraw <<'PY'
import json, sys
scene = json.load(open(sys.argv[1], encoding="utf-8"))
frames = [el for el in scene.get("elements", []) if el.get("type") == "frame"]
texts = [el for el in scene.get("elements", []) if el.get("type") == "text"]
if len(frames) != 4:
    raise SystemExit(f"expected 4 architecture columns, got {len(frames)}")
if not texts or any(el.get("fontFamily") != 2 for el in texts):
    raise SystemExit("minimal theme must use clean sans-serif text")
xs = [el["x"] for el in frames]
ys = [el["y"] for el in frames]
x2 = [el["x"] + el.get("width", 0) for el in frames]
y2 = [el["y"] + el.get("height", 0) for el in frames]
width, height = max(x2) - min(xs), max(y2) - min(ys)
if not 2.0 <= width / max(height, 1) <= 3.5:
    raise SystemExit(f"unexpected architecture aspect ratio: {width}x{height}")
PY
then log_pass "battery architecture uses four-column minimal visual system"; else log_fail "battery architecture visual system"; fi
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example thermal-runaway --output /tmp/e2e-hand-a.excalidraw >/dev/null 2>&1 && \
python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example thermal-runaway --output /tmp/e2e-hand-b.excalidraw >/dev/null 2>&1 && \
cmp -s /tmp/e2e-hand-a.excalidraw /tmp/e2e-hand-b.excalidraw && \
python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" /tmp/e2e-hand-a.excalidraw --visual --fail-on-warning >/dev/null 2>&1
if [ "$?" -eq 0 ]; then log_pass "thermal-runaway hand-drawn board is deterministic and strict-visual clean"; else log_fail "thermal-runaway hand-drawn board regression"; fi
if python3 - /tmp/e2e-hand-a.excalidraw <<'PY'
import json, sys
scene = json.load(open(sys.argv[1], encoding="utf-8"))
elements = scene.get("elements", [])
frames = [el for el in elements if el.get("type") == "frame"]
texts = [el for el in elements if el.get("type") == "text"]
arrows = [el for el in elements if el.get("type") == "arrow"]
shapes = [el for el in elements if el.get("type") in ("rectangle", "ellipse", "diamond")]
if len(frames) != 3 or len(arrows) != 8:
    raise SystemExit("hand-drawn board structure incomplete")
if not shapes or any(el.get("roughness", 0) < 2 for el in shapes):
    raise SystemExit("sketch shapes lost hand-drawn roughness")
if not {1, 12}.issubset({el.get("fontFamily") for el in texts}):
    raise SystemExit("Long Cang Chinese / Virgil English font hierarchy missing")
if not any("\n" in el.get("text", "") for el in texts):
    raise SystemExit("bilingual multiline text boxes missing")
if len({el.get("strokeColor") for el in arrows}) < 3:
    raise SystemExit("semantic arrow colors missing")
if not any(el.get("strokeStyle") == "dashed" for el in arrows):
    raise SystemExit("dashed mechanism arrow missing")
if not any(el.get("roundness") for el in arrows if len(el.get("points", [])) > 2):
    raise SystemExit("curved hand-drawn arrow missing")
if scene.get("appState", {}).get("cjkFontFamily") != "Long Cang":
    raise SystemExit("explicit Chinese handwriting font missing")
if not all(el.get("customData", {}).get("cjkFontFamily") == "Long Cang" for el in texts):
    raise SystemExit("Chinese handwriting metadata is not preserved on text elements")
PY
then log_pass "hand-drawn board preserves bilingual boxes and expressive arrows"; else log_fail "hand-drawn visual contract"; fi
HAND_FONT_OUT="/tmp/e2e-hand-font"
mkdir -p "$HAND_FONT_OUT"
if node "$PROJECT_DIR/scripts/render_preview.js" /tmp/e2e-hand-a.excalidraw "$HAND_FONT_OUT" \
    --format svg --no-server >/dev/null 2>&1 && \
  grep -q 'Long Cang' "$HAND_FONT_OUT/e2e-hand-a.svg" && \
  grep -q 'font-family="Virgil' "$HAND_FONT_OUT/e2e-hand-a.svg"; then
  log_pass "SVG renderer splits Chinese handwriting and English Virgil fonts"
else
  log_fail "CJK handwriting font render regression"
fi
if python3 "$PROJECT_DIR/scripts/validate_builtin_libraries.py" >/dev/null 2>&1; then
  log_pass "built-in library manifest and SHA-256"
else
  log_fail "built-in library manifest/hash validation"
fi
LIBRARY_ISOLATED=$(mktemp -d)
mkdir -p "$LIBRARY_ISOLATED/home" "$LIBRARY_ISOLATED/tmp"
if HOME="$LIBRARY_ISOLATED/home" TMPDIR="$LIBRARY_ISOLATED/tmp" \
  python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example architecture --library \
    --output "$LIBRARY_ISOLATED/architecture.excalidraw" >/dev/null 2>&1 && \
  HOME="$LIBRARY_ISOLATED/home" TMPDIR="$LIBRARY_ISOLATED/tmp" \
  python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" "$LIBRARY_ISOLATED/architecture.excalidraw" \
    --visual --fail-on-warning >/dev/null 2>&1; then
  log_pass "built-in --library works offline with isolated HOME/TMPDIR"
else
  log_fail "isolated built-in --library generation/validation"
fi
rm -rf "$LIBRARY_ISOLATED"
if python3 - "$PROJECT_DIR/scripts" <<'PY'
import pathlib, sys
sys.path.insert(0, sys.argv[1])
import library_loader

missing = []
for key, mapping in library_loader.LIBRARY_MAPPING.items():
    if mapping is not None and library_loader.lookup_component(key, key) is None:
        missing.append(key)
if missing:
    raise SystemExit(f"unresolved built-in mappings: {missing}")
PY
then log_pass "all configured library mappings resolve offline"; else log_fail "built-in library mapping coverage"; fi
if python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example architecture \
  --library-dir "$PROJECT_DIR/assets/builtin-libraries" \
  --output /tmp/e2e-library-override.excalidraw >/dev/null 2>&1; then
  log_pass "--library-dir explicit override"
else
  log_fail "--library-dir explicit override"
fi
if python3 - "$PROJECT_DIR/examples/microservice-arch-ir.json" "$PROJECT_DIR/scripts/ir_to_excalidraw.py" <<'PY'
import json, subprocess, sys, tempfile
ir_path, script = sys.argv[1:]
ir = json.load(open(ir_path, encoding="utf-8"))
out = "/tmp/e2e-library-semantic.excalidraw"
subprocess.run(["python3", script, ir_path, "--library", "--output", out], check=True, stdout=subprocess.DEVNULL)
scene = json.load(open(out, encoding="utf-8"))
texts = [e.get("text", "") for e in scene.get("elements", [])
         if e.get("type") == "text" and not str(e.get("id", "")).startswith("elbl-")]
bad = {n["label"]: sum(t == n["label"] for t in texts) for n in ir.get("nodes", []) if n.get("label")}
bad = {k: v for k, v in bad.items() if v != 1}
if bad:
    print("semantic label count mismatch:", bad, file=sys.stderr)
    raise SystemExit(1)
by_node = {e.get("customData", {}).get("libraryNodeId"): e for e in scene.get("elements", [])
           if e.get("type") == "text" and e.get("customData", {}).get("libraryTitle")}
elements = scene.get("elements", [])
for node in ir.get("nodes", []):
    if node.get("type") != "database":
        continue
    title = by_node.get(node["id"])
    if not title or title.get("strokeColor") in ("#fff", "#ffffff"):
        raise SystemExit(f"database title not visible: {node['id']}")
    groups = set(title.get("groupIds") or [])
    members = [e for e in elements if groups.intersection(e.get("groupIds") or []) and e.get("type") != "text"]
    if not members:
        raise SystemExit(f"database component bbox missing: {node['id']}")
    x, y = title["x"] + title["width"] / 2, title["y"] + title["height"] / 2
    if not any(e["x"] <= x <= e["x"] + e["width"] and e["y"] <= y <= e["y"] + e["height"] for e in members):
        raise SystemExit(f"database title outside component: {node['id']}")
    if node.get("type") == "database" and title.get("strokeColor") == "#ffffff":
        raise SystemExit(f"database title has low contrast: {node['id']}")
for node in ir.get("nodes", []):
    if node.get("type") == "actor":
        title = by_node.get(node["id"])
        if not title or title.get("strokeColor") != "#ffffff":
            raise SystemExit("actor title must use white text on the dark Person component")
PY
then log_pass "--library semantic labels exactly once"; else log_fail "--library semantic label completeness"; fi

# --- Test 12: Cloud architecture icon injection (C.7) ---
echo "=== Test 12: Icon library ==="
if python3 "$PROJECT_DIR/scripts/icon_library.py" --list >/dev/null 2>&1; then
  log_pass "icon_library.py lists tech icons"
else
  log_fail "icon_library.py --list"
fi

if python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" --example architecture --icons --output /tmp/e2e-icons.excalidraw >/dev/null 2>&1; then
  if grep -q '"type": "image"' /tmp/e2e-icons.excalidraw && grep -q '"files"' /tmp/e2e-icons.excalidraw; then
    log_pass "architecture --icons injects image elements + files"
  else
    log_fail "icons injection output missing image/files"
  fi
else
  log_fail "ir_to_excalidraw.py --icons"
fi

# --- Test 13: Animation GIF export (E.3) ---
echo "=== Test 13: Animation GIF export ==="
if python3 "$PROJECT_DIR/scripts/render_animation_gif.py" \
    "$PROJECT_DIR/output/example-flowchart-animated.excalidraw" \
    --output /tmp/e2e-animation.gif >/dev/null 2>&1; then
  if [ -s /tmp/e2e-animation.gif ] && head -c 6 /tmp/e2e-animation.gif | grep -q "GIF89a"; then
    log_pass "animation GIF exported (valid GIF89a)"
  else
    log_fail "animation GIF file invalid"
  fi
else
  log_fail "render_animation_gif.py (need pillow; cairosvg/rsvg-convert for frames)"
fi

echo "=== Test 14: Visual contract ==="
VISUAL_IR="$PROJECT_DIR/examples/visual-contract-ir.json"
VISUAL_OUT="/tmp/e2e-visual-contract.excalidraw"
if python3 "$PROJECT_DIR/scripts/ir_to_excalidraw.py" "$VISUAL_IR" --output "$VISUAL_OUT" >/dev/null 2>&1 \
  && python3 - "$VISUAL_OUT" <<'PY'
import json, sys
scene = json.load(open(sys.argv[1], encoding="utf-8"))
if "visual_contract" not in scene:
    raise SystemExit("visual_contract missing from output")
mapped = [e for e in scene["elements"] if e.get("customData", {}).get("visualFactIds")]
if not mapped or not all(e.get("customData", {}).get("visualSources") for e in mapped):
    raise SystemExit("visual fact/source mapping missing")
PY
then
  log_pass "IR conversion preserves visual contract mappings"
else
  log_fail "IR visual contract conversion"
fi
if python3 "$PROJECT_DIR/scripts/validate_excalidraw.py" "$VISUAL_OUT" --visual --fail-on-warning >/tmp/e2e-visual-contract.log 2>&1; then
  log_pass "visual contract strict validation"
else
  log_fail "visual contract strict validation (see /tmp/e2e-visual-contract.log)"
fi
if python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location("validator", "scripts/validate_excalidraw.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
warnings = []
mod._visual_checks([
    {"id": "a", "type": "rectangle", "x": 0, "y": 0, "width": 100, "height": 100},
    {"id": "b", "type": "rectangle", "x": 10, "y": 10, "width": 100, "height": 100},
    {"id": "dangling", "type": "arrow", "x": 0, "y": 0, "width": 10, "height": 0, "points": [[0, 0], [10, 0]]},
], warnings, {"visual_families": {"primary": "pipeline"}})
if not any("overlaps" in item for item in warnings) or not any("dangling" in item for item in warnings):
    raise SystemExit("_visual_checks regression coverage failed")
PY
then
  log_pass "_visual_checks overlap/dangling coverage"
else
  log_fail "_visual_checks overlap/dangling coverage"
fi
if python3 - <<'PY'
import importlib.util
import json

spec = importlib.util.spec_from_file_location("converter", "scripts/ir_to_excalidraw.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
base = json.load(open("examples/visual-contract-ir.json", encoding="utf-8"))

dangling = json.loads(json.dumps(base))
dangling["visual_contract"]["decisive_facts"][0]["targets"] = ["missing-node"]
duplicate_family = json.loads(json.dumps(base))
duplicate_family["visual_contract"]["visual_families"]["supporting"] = ["pipeline"]
for invalid in (dangling, duplicate_family):
    try:
        mod._visual_contract_annotations(invalid)
    except ValueError:
        continue
    raise SystemExit("invalid visual contract was accepted")
PY
then
  log_pass "visual contract rejects dangling targets and duplicate families"
else
  log_fail "visual contract rejection coverage"
fi

# --- Summary ---
echo ""
echo "=== Summary ==="
echo "  Pass: $pass  Warn: $warn  Fail: $fail"

if [ "$fail" -gt 0 ]; then
  exit 1
fi
exit 0
