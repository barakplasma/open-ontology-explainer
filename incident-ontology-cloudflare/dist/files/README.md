# Learn Open Ontologies through public vocabularies

This lab teaches ontology concepts and operations in [Open Ontologies](https://github.com/fabio-rovai/open-ontologies). A fictional security incident supplies example facts. The lessons cover the tool and the model, rather than incident-response procedures.

The visual site uses participant sequence diagrams: named participants, lifelines, ordered requests/replies and self-calls. Select a message to inspect the definition, RDF, query or engine result behind it. Mermaid sources are in `diagrams/`.

## Six operations to understand

| Lesson | What you learn | Tool |
| --- | --- | --- |
| Concepts | Definitions describe kinds of things; facts describe particular instances. | `onto_load` |
| Public terms | Compose public vocabulary with explicit local extensions. | Load the selected definitions. |
| Query | Match linked facts using SPARQL. | `onto_query` |
| Validate | Check declared names separately from application value constraints. | `onto_vocab_check`, `onto_shacl` |
| Reason | Materialize consequences of a class/property hierarchy. | `onto_reason` |
| Plan changes | Preview what an edit changes before applying it. | `onto_plan` |

These are MCP tool names. The runnable script uses their CLI counterparts. A Go orchestrator can connect to the MCP server without running a Python service.

## Public vocabulary actually used in the RDF

| Public terms | Use |
| --- | --- |
| `schema:Person`, `schema:name` | Dana and eight other fictional people. |
| `schema:Organization` | SOC and IT organizations. |
| `schema:OrganizationRole`, `schema:member`, `schema:roleName` | Qualified memberships and incident assignments. |
| `schema:Action`, `schema:agent`, `schema:object`, `schema:actionStatus` | A shared model of a proposed action. |
| `schema:Product`, `schema:Service`, `schema:identifier` | Workstation, business service and evidence IDs. |
| `prov:Entity`, `prov:wasDerivedFrom`, `prov:wasAttributedTo` | Finding records, evidence and attribution. |

`schema:` means `https://schema.org/`; `prov:` means `http://www.w3.org/ns/prov#`. Our extension uses `ir:` at `https://example.org/incident#`. Fictional instance IDs use `ex:`.

```turtle
ex:Dana a schema:Person ; schema:name "Dana" .

ir:IncidentAssignment
    rdfs:subClassOf schema:OrganizationRole .

ex:SOCAssignment a ir:IncidentAssignment ;
    schema:member ex:Dana ;
    schema:roleName "SOC analyst" ;
    ir:forIncident ex:INC001 .
```

Schema.org documents the intermediate OrganizationRole pattern: an organization's member can be a role, whose member is a person. The example uses this for SOC and IT. The local class and `ir:forIncident` add our specific incident scope. A role assignment has its own identity and properties.

The local `ir:supportedBy` relation is a subproperty of `prov:wasDerivedFrom`. Reasoning supplies that public provenance relation, making it available to a consumer using PROV-O. It describes the recorded claim's derivation; it does not establish that claim's truth.

## Files

- `public-vocabulary.ttl`: 72 selected RDF statements from official Schema.org and W3C PROV-O files.
- `vocabulary-sources.json`: retrieval URLs, SHA-256 digests and selected terms.
- `ontology.ttl`: local classes, properties, subclasses and subproperties.
- `facts.ttl`: concrete instance data.
- `incident.ttl`: the combined standalone fixture.
- `shapes.ttl`: application constraints in SHACL.
- `invented-predicate.ttl`: an undeclared field proposal.
- `wrong-name-proposal.ttl`: a declared name field with numeric value 42.
- `queries/`: nine SPARQL examples, including public people, roles and provenance.
- `output/results.json`: observed native outputs and the semantic plan.
- `output/certificate/`: generated inference certificate, not independently verified here.
- `diagrams/`: participant diagrams exported as Mermaid sequence sources.

The public snapshot contains selected declarations and relevant hierarchy/domain/range statements. It is not a complete import of either vocabulary and does not claim their full OWL semantics. Official source files were retrieved on 2026-10-27 and hashed. A prefix abbreviates IRIs; it does not import or download definitions.

## Run the library

Install [Open Ontologies v2.1.0](https://github.com/fabio-rovai/open-ontologies/releases/tag/v2.1.0), then run:

```bash
OO_BIN=/absolute/path/to/open-ontologies python3 run_demo.py
```

The wrapper needs only Python's standard library. No LLM key or GPU is required. It creates fresh temporary stores, then writes results to `output/`.

For manual CLI use, make persistence explicit so separate processes share a store:

```bash
export OPEN_ONTOLOGIES_STORAGE_MODE=persistent
open-ontologies --data-dir ./lab-store --no-connect load incident.ttl
open-ontologies --data-dir ./lab-store --no-connect reason --profile rdfs
open-ontologies --data-dir ./lab-store --no-connect query - < queries/07-public-roles.rq
open-ontologies --data-dir ./lab-store --no-connect shacl shapes.ttl
```

The MCP server starts with `open-ontologies serve`. See the [quickstart](https://github.com/fabio-rovai/open-ontologies/blob/main/docs/quickstart.md) and [tool reference](https://github.com/fabio-rovai/open-ontologies/blob/main/docs/tool-reference.md).

## Observed results and their meaning

The released Linux v2.1.0 engine loaded **431 asserted triples**, materialized **116 RDFS consequences**, and returned nine people/role rows using Schema.org terms. The PROV-O query returned the synthetic EDR source, Dana as author and a Suspected status.

Vocabulary checking accepted the declared fields and rejected `ir:jobTitleLabel`. It also accepted the field name `schema:name` with value 42: checking vocabulary names does not check our value constraint. SHACL rejected that numeric name because our shape requires `xsd:string`. The valid fixture passed eight shapes with 27 focus nodes and no unmatched shapes.

An ASK for `ex:IsolateLaptop a schema:Action` returned false before materialization and true afterward. The earlier false reports the absence of a stored triple; it does not prove that the ontology entails its negation.

The deliberately wrong subclass proposal added one assertion. `plan` reported two new consequences under its OWL-RL table: the assertion and a new inferred classification of PausePayroll. No change was applied. Its low structural risk score did not establish that the new definition had the intended meaning.

The independent proof checker failed at startup with `failed to locate application`. Certificates and semantic-plan findings are **engine output, not independently verified claims** in this lab. Even an accepted certificate would establish consequences of supplied premises, not the authenticity of evidence or human approval.

## Public sources

- [Schema.org Person](https://schema.org/Person)
- [Schema.org OrganizationRole and membership examples](https://schema.org/OrganizationRole)
- [Schema.org Role](https://schema.org/Role)
- [Schema.org Action](https://schema.org/Action)
- [Official Schema.org RDF](https://schema.org/version/latest/schemaorg-current-https.ttl)
- [W3C PROV-O Recommendation](https://www.w3.org/TR/prov-o/)
- [Official PROV-O RDF](https://www.w3.org/ns/prov-o.ttl)

Your application remains responsible for accepting facts, controlling visibility and authorizing execution. Public vocabulary provides shared meaning; the engine does not establish that all supplied facts are true.
