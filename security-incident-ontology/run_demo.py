#!/usr/bin/env python3
"""Run the released Rust engine. Python is only a standard-library CLI wrapper.

OO_BIN=/path/to/open-ontologies python3 run_demo.py
Optional: OO_CERT=/path/to/oo-cert to independently check the RDFS certificate.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BINARY = shutil.which(os.environ.get("OO_BIN", "open-ontologies"))
if not BINARY:
    raise SystemExit("Install Open Ontologies v2.1.0, then set OO_BIN or add it to PATH. See README.md.")


def run(store, *args, ok_codes=(0,)):
    result = subprocess.run(
        [BINARY, "--data-dir", str(store), "--no-connect", *args],
        env={**os.environ, "OPEN_ONTOLOGIES_STORAGE_MODE": "persistent"},
        text=True, capture_output=True,
    )
    if result.returncode not in ok_codes:
        raise RuntimeError(f"{args[0]} exited {result.returncode}\n{result.stdout}\n{result.stderr}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Non-JSON output from {args[0]}: {result.stdout}\n{result.stderr}") from error
    return result.returncode, payload


def main():
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    results = {}
    # Each run has its own empty store, so repeated runs cannot retain old facts.
    with tempfile.TemporaryDirectory(prefix="incident-demo-") as temporary:
        store = Path(temporary) / "valid-store"
        _, results["load"] = run(store, "load", str(ROOT / "incident.ttl"))
        query = (ROOT / "queries/05-inference.rq").read_text()
        _, results["before_reasoning"] = run(store, "query", query)
        _, results["public_before_reasoning"] = run(store, "query", (ROOT / "queries/09-public-inference.rq").read_text())
        _, results["reasoning"] = run(store, "reason", "--profile", "rdfs", "--certificate", str(out / "certificate"))
        _, results["valid_shapes"] = run(store, "shacl", str(ROOT / "shapes.ttl"))
        for query_file in sorted((ROOT / "queries").glob("*.rq")):
            _, results[query_file.stem] = run(store, "query", query_file.read_text())

        # A separate store holds the deliberately invalid approval.
        bad_data = Path(temporary) / "invalid.ttl"
        bad_data.write_text((ROOT / "incident.ttl").read_text() + "\n" + (ROOT / "invalid-approval.ttl").read_text())
        bad_store = Path(temporary) / "invalid-store"
        run(bad_store, "load", str(bad_data))
        run(bad_store, "reason", "--profile", "rdfs")
        code, results["invalid_shapes"] = run(bad_store, "shacl", str(ROOT / "shapes.ttl"), ok_codes=(1,))
        results["invalid_shapes_exit_code"] = code

        # Public vocabulary declarations are loaded separately from instance data.
        definitions = Path(temporary) / "definitions.ttl"
        definitions.write_text((ROOT / "public-vocabulary.ttl").read_text() + "\n" + (ROOT / "ontology.ttl").read_text())
        definition_store = Path(temporary) / "definition-store"
        run(definition_store, "load", str(definitions))
        _, results["vocab_valid"] = run(definition_store, "vocab-check", str(ROOT / "facts.ttl"))
        _, results["vocab_invented"] = run(definition_store, "vocab-check", str(ROOT / "invented-predicate.ttl"), ok_codes=(0, 1))
        _, results["vocab_name_value"] = run(definition_store, "vocab-check", str(ROOT / "wrong-name-proposal.ttl"))

        # Schema.org supplies meaning; this application's SHACL adds a type rule.
        original = (ROOT / "incident.ttl").read_text()
        wrong_name = Path(temporary) / "wrong-name.ttl"
        wrong_name.write_text(original.replace('schema:name "Dana"', 'schema:name 42'))
        assert wrong_name.read_text() != original
        wrong_name_store = Path(temporary) / "wrong-name-store"
        run(wrong_name_store, "load", str(wrong_name))
        run(wrong_name_store, "reason", "--profile", "rdfs")
        _, results["invalid_name_shapes"] = run(wrong_name_store, "shacl", str(ROOT / "shapes.ttl"), ok_codes=(1,))

        # A deliberately bad classification edit is planned, never applied.
        proposed = Path(temporary) / "proposed.ttl"
        proposed.write_text(original + "\n<https://example.org/incident#ServicePauseAction> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <https://example.org/incident#EndpointIsolationAction> .\n")
        plan_store = Path(temporary) / "plan-store"
        run(plan_store, "load", str(ROOT / "incident.ttl"))
        _, results["change_plan"] = run(plan_store, "plan", str(proposed))

    checker = shutil.which(os.environ.get("OO_CERT", "oo-cert"))
    if checker:
        check = subprocess.run(
            [checker, str(out / "certificate/asserted.tsv"), str(out / "certificate/derivations.tsv")],
            text=True, capture_output=True,
        )
        try:
            check_report = json.loads(check.stdout)
        except json.JSONDecodeError:
            check_report = {"output": check.stdout.strip(), "stderr": check.stderr.strip()}
        results["independent_certificate_check"] = {
            "checked": check.returncode == 0 and check_report.get("ok") is True,
            "exit_code": check.returncode, "report": check_report,
        }
    else:
        results["independent_certificate_check"] = {"checked": False, "note": "Certificate written; oo-cert was not found."}

    # These checks are the educational contract of the example.
    assert results["before_reasoning"]["result"] is False
    assert results["05-inference"]["result"] is True
    assert results["public_before_reasoning"]["result"] is False
    assert results["09-public-inference"]["result"] is True
    assert len(results["06-public-people"]["results"]) == 9
    assert len(results["07-public-roles"]["results"]) == 9
    assert results["invalid_name_shapes"]["conforms"] is False
    assert results["vocab_valid"]["conforms"] is True
    assert results["vocab_name_value"]["conforms"] is True
    assert results["vocab_invented"]["conforms"] is False
    assert results["vocab_invented"]["hallucinated_terms"] == ["https://example.org/incident#jobTitleLabel"]
    assert results["change_plan"]["triple_delta"]["insertions"] == 1
    assert any(row["triple"][0] == "<https://example.org/demo/PausePayroll>" for row in results["change_plan"]["conservativity"]["new_consequences_over_old_signature"])
    assert results["reasoning"]["inferred_count"] > 0
    assert results["valid_shapes"]["conforms"] is True
    assert results["valid_shapes"]["focus_nodes"] > 0
    assert results["valid_shapes"]["unmatched_shapes"] == []
    assert results["invalid_shapes"]["conforms"] is False
    assert any(v["focus_node"].endswith("/WrongRoleGrant") for v in results["invalid_shapes"]["violations"])
    assert len(results["01-roster"]["results"]) == 9
    decisions = {row["action"].strip('"'): row["decisionState"].strip('"') for row in results["03-action-decisions"]["results"]}
    assert decisions == {"Isolate Laptop-42": "Matching grant recorded", "Pause Payroll": "No matching grant recorded"}
    assert results["04-findings"]["results"][0]["status"] == '"Suspected"'

    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    print(f"\nResults and inference certificate: {out}")


if __name__ == "__main__":
    main()
