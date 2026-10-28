# Open Ontologies Visual Lab

An interactive guide to ontology concepts and the Open Ontologies library. A fictional incident supplies example data. The existing `incident-ontology` Cloudflare Worker hosts the page.

Six participant-diagram lessons cover Concepts, Public terms, Query, Validate, Reason and Plan changes. The RDF actually uses Schema.org for people, organizations, roles and actions, and W3C PROV-O for provenance. Engine outputs are recorded; conceptual extraction and application handoffs are labeled.

The root page is a plain-English manager’s guide with a participant sequence, comparison table, costs and pilot criteria. `/lab.html` hosts the original six lessons. Existing root URLs containing `?lesson=` remain supported.

## Source

- `dist/lessons.js`: semantic model and Mermaid sequence export.
- `dist/sequence-app.js`: message selection, URL state and SVG sequence renderer.
- `dist/sequence.css`: participant-diagram styles.
- `dist/index.html`, `dist/style.css`: shell and base styles.
- `export-diagrams.mjs`: exports the six Mermaid participant diagrams.
- `build.py`: bundles assets and the example into `worker.mjs`.
- `wrangler.toml`: deployment configuration without credentials.

The renderer preserves lifelines, ordered requests/replies and self-calls. Narrow screens horizontally scroll the diagram at readable sizes; Fit gives an optional overview. Controls and messages support keyboard interaction. The URL preserves lesson, one-based message number, proposal variant, reasoning replay and view settings.

The site does not run the native engine or make model calls. Its outputs come from the adjacent `security-incident-ontology/run_demo.py`. The source archive contains that fixture. Public definitions are a documented selected snapshot, not a full vocabulary import.

## Rebuild

```bash
OO_BIN=/path/to/open-ontologies python3 ../security-incident-ontology/run_demo.py
node export-diagrams.mjs
python3 build.py
npx wrangler deploy
```

Repack the example ZIP after editing its sources when updating the download. The current deployment uses the connected Cloudflare API. The generated Worker is self-contained.
