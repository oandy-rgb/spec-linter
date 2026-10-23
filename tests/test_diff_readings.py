import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("diff_readings", ROOT / "scripts" / "diff_readings.py")
diff_readings = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diff_readings)

FIXTURE = ROOT / "tests" / "fixtures" / "withdrawal_readings"


class DiffReadingsTest(unittest.TestCase):
    def test_finds_limit_and_approval_disagreements(self):
        result = diff_readings.diff(diff_readings.load_readings(FIXTURE), max_cases=20000)
        rows = result["divergences"]
        self.assertTrue(rows)
        # Inputs from all readings are merged, with integer neighbours added.
        self.assertIn(10001, result["inputs"]["amount"])
        # An approved withdrawal over $10,000: allowed literally and adversarially,
        # rejected by the operational daily limit (the approval clause is unreachable).
        unreachable = [
            case
            for r in rows
            if r["outcomes"] == {"adversarial": "allowed", "literal": "allowed", "operational": "rejected:limit"}
            for case in r["examples"]
            if case["amount"] > 10000 and case["approved"]
        ]
        self.assertTrue(unreachable)
        # Patterns that split the readings into more groups come first.
        groups = [r["groups"] for r in rows]
        self.assertEqual(groups, sorted(groups, reverse=True))

    def test_three_way_split_ranks_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, label in (("a", "x"), ("b", "y"), ("c", "z")):
                (Path(tmp) / f"{name}.py").write_text(
                    "INPUTS = {'n': [0, 10]}\n"
                    f"def outcome(case):\n    return '{label}' if case['n'] > 5 else ('x' if '{name}' == 'a' else 'y')\n"
                )
            rows = diff_readings.diff(diff_readings.load_readings(Path(tmp)), max_cases=1000)["divergences"]
            self.assertEqual([r["groups"] for r in rows], [3, 2])

    def test_numbers_in_labels_do_not_split_patterns(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.py").write_text("INPUTS = {'n': [0, 10, 20]}\ndef outcome(case):\n    return f\"fee={case['n']}\"\n")
            (Path(tmp) / "b.py").write_text("INPUTS = {}\ndef outcome(case):\n    return f\"fee={case['n'] * 2}\"\n")
            rows = diff_readings.diff(diff_readings.load_readings(Path(tmp)), max_cases=1000)["divergences"]
            self.assertEqual(len(rows), 1)

    def test_non_negative_values_get_no_negative_neighbours(self):
        values = diff_readings.candidate_values({"r": ({"n": [0, -3]}, None)})
        self.assertEqual(values["n"], [0, -3, 1, -4, -2])

    def test_identical_readings_do_not_diverge(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("a", "b"):
                shutil.copy(FIXTURE / "operational.py", Path(tmp) / f"{name}.py")
            result = diff_readings.diff(diff_readings.load_readings(Path(tmp)), max_cases=1000)
            self.assertEqual(result["divergences"], [])

    def test_reading_errors_are_reported_as_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(FIXTURE / "literal.py", Path(tmp) / "a.py")
            (Path(tmp) / "b.py").write_text("INPUTS = {'amount': [1]}\ndef outcome(case):\n    return case['missing']\n")
            result = diff_readings.diff(diff_readings.load_readings(Path(tmp)), max_cases=1000)
            self.assertTrue(any(r["outcomes"]["b"].startswith("ERROR") for r in result["divergences"]))


if __name__ == "__main__":
    unittest.main()
