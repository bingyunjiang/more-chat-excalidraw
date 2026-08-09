# Built-in Excalidraw Library

`core.excalidrawlib` is an original, self-authored component set distributed
with this skill under the repository's MIT license. It provides the default
offline C4-style, Kubernetes, AWS Serverless, and BPMN mappings used by
`--library`; users do not need to download a separate Library.

`manifest.json` records the package version, provenance, license, and SHA-256.
Run `python3 scripts/validate_builtin_libraries.py` from the repository root to
verify the asset and required item set.

Custom or third-party `.excalidrawlib` files are not bundled here. They can be
selected explicitly with `--library-dir <directory>` and require their own
license review.
