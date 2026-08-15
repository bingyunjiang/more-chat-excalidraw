# Video Storyboard Delivery Profile

`video-storyboard` is a delivery profile, not an additional diagram template.
Each frame may use a different content template while sharing the same canvas
size, theme, typography, brand area, and animation contract.

## Minimal IR

```json
{
  "version": 2,
  "delivery": {
    "profile": "video-storyboard",
    "frameWidth": 1600,
    "frameHeight": 900,
    "safeMargin": 60,
    "gutter": 120
  },
  "shared": {
    "theme": "sketch",
    "sketchStyle": "engineering-notebook",
    "typography": {
      "titleZh": {"fontFamily": 11, "fontSize": 42},
      "bodyZh": {"fontFamily": 12, "fontSize": 23},
      "titleEn": {"fontFamily": 1, "fontSize": 20},
      "bodyEn": {"fontFamily": 1, "fontSize": 18},
      "caption": {"fontFamily": 1, "fontSize": 14},
      "edgeLabel": {"fontFamily": 1, "fontSize": 32}
    }
  },
  "frames": [
    {
      "id": "frame-01",
      "title": "开场",
      "template": "relationship",
      "nodes": [],
      "edges": [],
      "speakerNotes": "",
      "cameraCue": ""
    }
  ]
}
```

## Rules

- Each frame is 16:9 by default and is exported independently when `--frames`
  is used.
- A bilingual card uses one shape plus grouped independent text layers. Do not
  bind multiple text elements to the same Excalidraw container.
- `safeMargin` applies after frame translation and rotation.
- `angle` in the Excalidraw scene remains radians. User-facing builders should
  prefer `angleDeg` and convert once.
- `speakerNotes`, `cameraCue`, and `estimatedDuration` remain in the storyboard
  metadata and do not become visible diagram text automatically.

## Export

```bash
node scripts/render_preview.js output/storyboard.excalidraw \
  output/storyboard-render \
  --format both --frames --contact-sheet --require-native --require-png
```

The export directory contains one scene preview per frame, a complete board
preview, a render manifest, and a storyboard QA report. Fallback SVG output is
marked as such and cannot satisfy `--require-native`.
