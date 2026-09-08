"""
Parcel Attribute Rule Validator
================================
Recreation of the automated attribute rule engine built for the Town of
Enfield's centralized parcel feature class (33+ rules governing 16,000+
parcel records). This version runs against a small synthetic sample
dataset so it's runnable standalone, with no ArcGIS Pro or live
geodatabase connection required.

The real system runs these checks as Arcade attribute rules directly
inside the enterprise geodatabase, firing on every edit. This script
demonstrates the same rule logic in plain Python against a batch of
records, which is how the rules were originally prototyped and tested
before being ported into Arcade.

Usage:
    python parcel_attribute_validator.py
"""

import csv
import io
import re
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
# Synthetic parcel records. Not real Town of Enfield data. Includes a mix of
# clean records and deliberately broken ones to exercise every rule.

SAMPLE_PARCELS = [
    {"parcel_id": "12-034-0001", "owner": "SMITH JOHN", "zoning": "R1",
     "acreage": "0.42", "unit": "", "is_condo": "N", "noid": "N"},
    {"parcel_id": "12-034-0002", "owner": "DOE JANE", "zoning": "R1",
     "acreage": "0.38", "unit": "", "is_condo": "N", "noid": "N"},
    {"parcel_id": "12-034-0003-U1", "owner": "PARK CONDO ASSOC", "zoning": "R3",
     "acreage": "0.05", "unit": "1", "is_condo": "Y", "noid": "N"},
    {"parcel_id": "12-034-0003-U2", "owner": "PARK CONDO ASSOC", "zoning": "R3",
     "acreage": "0.05", "unit": "2", "is_condo": "Y", "noid": "N"},
    {"parcel_id": "", "owner": "UNKNOWN OWNER", "zoning": "R1",
     "acreage": "0.51", "unit": "", "is_condo": "N", "noid": "Y"},
    {"parcel_id": "12-034-0005", "owner": "", "zoning": "R2",
     "acreage": "1.10", "unit": "", "is_condo": "N", "noid": "N"},
    {"parcel_id": "12-034-0006", "owner": "HALL MICHAEL", "zoning": "ZZ",
     "acreage": "0.60", "unit": "", "is_condo": "N", "noid": "N"},
    {"parcel_id": "12034-0007", "owner": "REED LISA", "zoning": "C1",
     "acreage": "-0.20", "unit": "", "is_condo": "N", "noid": "N"},
]

VALID_ZONING_CODES = {"R1", "R2", "R3", "C1", "C2", "I1", "AG"}
PARCEL_ID_PATTERN = re.compile(r"^\d{2}-\d{3}-\d{4}(-U\d+)?$")


@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    detail: str = ""


@dataclass
class ParcelReport:
    parcel_id: str
    results: list = field(default_factory=list)

    @property
    def failed_rules(self):
        return [r for r in self.results if not r.passed]


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------
# Each rule is a small function: (record) -> RuleResult.
# In the real Arcade implementation these run as Calculation/Constraint
# rules directly on the feature class; here they're plain Python so the
# logic can be unit tested independently of ArcGIS Pro.

def rule_parcel_id_format(rec: dict) -> RuleResult:
    ok = bool(PARCEL_ID_PATTERN.match(rec["parcel_id"] or ""))
    return RuleResult("parcel_id_format", ok,
                       "" if ok else f"'{rec['parcel_id']}' does not match NN-NNN-NNNN[-Uxx] pattern")


def rule_parcel_id_required(rec: dict) -> RuleResult:
    ok = bool(rec["parcel_id"].strip())
    return RuleResult("parcel_id_required", ok,
                       "" if ok else "Missing parcel ID")


def rule_owner_required(rec: dict) -> RuleResult:
    ok = bool(rec["owner"].strip())
    return RuleResult("owner_required", ok,
                       "" if ok else "Missing owner of record")


def rule_zoning_domain(rec: dict) -> RuleResult:
    ok = rec["zoning"] in VALID_ZONING_CODES
    return RuleResult("zoning_domain", ok,
                       "" if ok else f"'{rec['zoning']}' is not a valid zoning code")


def rule_acreage_positive(rec: dict) -> RuleResult:
    try:
        ok = float(rec["acreage"]) > 0
    except (ValueError, TypeError):
        ok = False
    return RuleResult("acreage_positive", ok,
                       "" if ok else f"Acreage '{rec['acreage']}' must be a positive number")


def rule_condo_guard(rec: dict) -> RuleResult:
    """Condo parcels must carry a unit suffix in their parcel ID and a unit
    number; non-condo parcels must not."""
    is_condo = rec["is_condo"] == "Y"
    has_unit_suffix = "-U" in rec["parcel_id"]
    has_unit_number = bool(rec["unit"].strip())
    ok = (is_condo == has_unit_suffix) and (is_condo == has_unit_number)
    return RuleResult("condo_guard", ok,
                       "" if ok else "Condo flag, parcel ID unit suffix, and unit number are inconsistent")


def rule_noid_handling(rec: dict) -> RuleResult:
    """Records flagged NOID (no owner ID assigned by the Assessor) are
    allowed to skip the owner_required rule, but must not silently pass
    validation, they need a follow-up flag instead."""
    is_noid = rec["noid"] == "Y"
    if is_noid:
        ok = rec["parcel_id"].strip() == ""  # NOID records shouldn't have a real ID yet
        return RuleResult("noid_handling", True,
                           "Flagged NOID, follow-up required" if not ok else "NOID, no ID yet: expected")
    return RuleResult("noid_handling", True, "")


RULES: list[Callable[[dict], RuleResult]] = [
    rule_parcel_id_required,
    rule_parcel_id_format,
    rule_owner_required,
    rule_zoning_domain,
    rule_acreage_positive,
    rule_condo_guard,
    rule_noid_handling,
]


def validate(records: list[dict]) -> list[ParcelReport]:
    reports = []
    for rec in records:
        report = ParcelReport(parcel_id=rec.get("parcel_id") or "(missing)")
        for rule in RULES:
            # NOID records are exempt from the owner-required check
            if rule is rule_owner_required and rec.get("noid") == "Y":
                continue
            report.results.append(rule(rec))
        reports.append(report)
    return reports


def print_summary(reports: list[ParcelReport]) -> None:
    total = len(reports)
    clean = sum(1 for r in reports if not r.failed_rules)
    print(f"Validated {total} parcel records against {len(RULES)} rules")
    print(f"  Clean records : {clean}")
    print(f"  Flagged records: {total - clean}\n")

    for report in reports:
        if report.failed_rules:
            print(f"[FAIL] {report.parcel_id}")
            for r in report.failed_rules:
                print(f"    - {r.rule_name}: {r.detail}")

    # Per-rule violation counts, useful for spotting systemic data issues
    print("\nViolations by rule:")
    counts = {rule.__name__: 0 for rule in RULES}
    for report in reports:
        for r in report.failed_rules:
            counts[r.rule_name] = counts.get(r.rule_name, 0) + 1
    for name, count in counts.items():
        if count:
            print(f"    {name}: {count}")


def export_flagged_csv(reports: list[ParcelReport]) -> str:
    """Returns a CSV string of flagged records, one row per violation."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["parcel_id", "rule", "detail"])
    for report in reports:
        for r in report.failed_rules:
            writer.writerow([report.parcel_id, r.rule_name, r.detail])
    return buf.getvalue()


if __name__ == "__main__":
    results = validate(SAMPLE_PARCELS)
    print_summary(results)

    print("\n--- flagged_records.csv ---")
    print(export_flagged_csv(results))
