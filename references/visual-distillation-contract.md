# Visual distillation contract

`visual_contract` is an optional IR section for diagrams whose visual meaning
must remain traceable to source material. It is a contract about what the
canvas is allowed to communicate, not an Excalidraw styling dump.

```json
{
  "visual_contract": {
    "decisive_facts": [{
      "id": "fact-intake",
      "statement": "The intake service is the first processing step.",
      "refs": ["brief:p2"], "targets": ["n1", "e1"],
      "semanticRole": "primary-flow", "family": "pipeline",
      "status": "proposed"
    }],
    "preserve": ["first-step ordering"],
    "allowed_abstraction": ["collapse repeated retry arrows"],
    "forbidden_invention": ["do not add an unreferenced service"],
    "layout_signals": {"direction": "left-to-right", "allowed_colors": ["#ffffff"]},
    "visual_families": {"primary": "pipeline", "supporting": ["group"]}
  }
}
```

`decisive_facts` contains 3–6 objects. Each fact has a stable `id`, a
`statement`, unique provenance `refs`, and one or more unique `targets` naming
existing IR node or edge IDs. Dangling target IDs block conversion.
`semanticRole` and `family` are optional labels. `preserve`,
`allowed_abstraction`, and `forbidden_invention` state respectively what must
survive, what simplification is permitted, and what the renderer must not add.

`layout_signals` describes visual guidance such as direction, emphasis,
grouping, and optionally `allowed_colors`. `visual_families.primary` is
required; `supporting` has at most two distinct non-primary names. A fact may select one
of these families, otherwise its target uses the primary family.

Facts and boundary entries may carry `status`: exactly `proposed` or
`confirmed`. Omitted status means `proposed`; conversion never upgrades a
proposal. When the contract is present, relevant elements receive
`customData.semanticRole`, `visualFactIds`, `visualSources`, `visualFamily`,
and `visualStatus`. When absent, legacy conversion is unchanged.
