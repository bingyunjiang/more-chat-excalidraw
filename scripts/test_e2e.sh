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
if [ ! -f "$MINIMAL" ]; then
  echo '{"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":[{"id":"r1","type":"rectangle","x":0,"y":0,"width":100,"height":60,"strokeColor":"#1e1e1e","backgroundColor":"#ffffff","fillStyle":"solid","strokeWidth":1,"roughness":0,"opacity":100,"angle":0,"seed":1,"groupIds":[],"boundElements":[],"updated":1,"link":null,"locked":false}],"appState":{"viewBackgroundColor":"#ffffff"}}' > "$MINIMAL"
fi
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
else
  log_fail "preview server failed to start"
  cat "$PREVIEW_LOG" 2>/dev/null | tail -5
fi

kill "$PREVIEW_PID" 2>/dev/null
wait "$PREVIEW_PID" 2>/dev/null
echo "--- preview server log ---"
cat "$PREVIEW_LOG" 2>/dev/null | tail -3

# --- Summary ---
echo ""
echo "=== Summary ==="
echo "  Pass: $pass  Warn: $warn  Fail: $fail"

if [ "$fail" -gt 0 ]; then
  exit 1
fi
exit 0
