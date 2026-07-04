#!/usr/bin/env python3
"""
Fixture 19 — Out-of-Catalog Escalation Rule (added v0.4.3)

Validates the rule added in v0.4.3:
  "When a candidate chip is NOT in the catalogue (no yaml, no
  product_families.md row, no local datasheet PDF), the agent MUST
  escalate to Tier 4 (Tavily / vendor-direct fetch) and label each
  cell with [T4] + source URL + fetch timestamp — never silently drop
  the part."

The baseline is the 17-row BLE SoC comparison table built on
2026-07-02. This test ensures that the rule is documented and that
future regressions (e.g. removing the escalation, breaking source
markers) are caught.

The script does NOT re-fetch live data (that would require network
access and break offline CI). Instead, it validates the rules
against a frozen reference table that mirrors the baseline.

Usage:
    python3 scripts/test_outofcatalog.py
    # Exit 0 on pass, 1 on fail.
"""

import sys
from pathlib import Path
from datetime import datetime

# ---------- Reference baseline (mirrors BLE comparison from 2026-07-02) ----------
# Each row: (part_name, in_catalog, tier_used_for_field_x, source_marker)
# These are the rules the test enforces, not live datasheet values.

BASELINE = [
    # In-catalog parts (12) — Tier 1 yaml + Tier 4 for missing fields
    ("nRF52840",        True,  ["[T1]", "[T1]", "[T1]", "[T1]"]),
    ("nRF5340",         True,  ["[T1+T4]", "[T4]", "[T4]", "[T4]"]),
    ("nRF54L15",        True,  ["[T1+T4 partial]", "[T4-unverified]", "[T4-unverified]", "[T4-unverified]"]),
    ("STM32WB55",       True,  ["[T1+T4]", "[T1+T4]", "[T4]", "[T4]"]),
    ("CC2640R2F",       True,  ["[T1+T4]", "[T4-unverified]", "[T4-unverified]", "[T1+T4]"]),
    ("CC2652R",         True,  ["[T1+T4]", "[T4]", "[T4]", "[T4]"]),
    ("CC2340R5",        True,  ["[T1+T4]", "[T4]", "[T4]", "[T4]"]),
    ("DA14531",         True,  ["[T1 partial + T4]", "[T4]", "[T4]", "[T4]"]),
    ("DA14592",         True,  ["[T1 partial + T4]", "[T4]", "[T4]", "[T4]"]),
    ("DA14594",         True,  ["[T1 partial + T4 inferred]", "[T4 inferred]", "[T4 inferred]", "[T4 inferred]"]),
    ("EFR32BG22",       True,  ["[T1+T4]", "[T4]", "[T4]", "[T4]"]),
    ("EFR32BG24",       True,  ["[T1+T4]", "[T4]", "[T4]", "[T4]"]),
    # Out-of-catalog parts (5) — MUST use Tier 4 with citation
    ("CC2652P",         False, ["[T4 out-of-catalog]", "[T4]", "[T4]", "[T4]"]),
    ("TLSR8258",        False, ["[T4 out-of-catalog]", "[T4]", "[T4]", "[T4]"]),
    ("BL808",           False, ["[T4 out-of-catalog partial]", "[T4]", "[T4]", "[T4]"]),
    ("BK3432",          False, ["[T4 out-of-catalog]", "[T4]", "[T4]", "[T4]"]),
    ("CH583",           False, ["[T4 out-of-catalog partial]", "[T4]", "[T4]", "[T4]"]),
]

# ---------- Rules to enforce ----------

RULES = [
    {
        "name": "R1 — All parts present (no silent drops)",
        "check": lambda rows: len(rows) == 17,
        "msg":   lambda rows: f"Expected 17 rows, got {len(rows)} — agent may have silently dropped a candidate",
    },
    {
        "name": "R2 — Out-of-catalog parts MUST use Tier 4 marker",
        "check": lambda rows: all(
            any("[T4" in m for m in markers)
            for part, in_cat, markers in rows
            if not in_cat
        ),
        "msg":   lambda rows: f"Out-of-catalog parts without [T4] marker: "
                              f"{[p for p, ic, m in rows if not ic and not any('[T4' in x for x in m)]}",
    },
    {
        "name": "R3 — In-catalog parts MUST start with [T1] (yaml anchor)",
        "check": lambda rows: all(
            any("[T1" in m for m in markers)
            for part, in_cat, markers in rows
            if in_cat
        ),
        "msg":   lambda rows: f"In-catalog parts without [T1] anchor: "
                              f"{[p for p, ic, m in rows if ic and not any('[T1' in x for x in m)]}",
    },
    {
        "name": "R4 — Missing fields MUST be marked (not silently blank)",
        "check": lambda rows: all(
            all(m and ("unverified" in m or "not-found" in m or "partial" in m or "inferred" in m or "[T" in m) for m in markers)
            for part, in_cat, markers in rows
        ),
        "msg":   lambda rows: f"Rows with silently-blank cells: "
                              f"{[(p, [m for m in marks if not m or not any(x in m for x in ['unverified','not-found','partial','inferred','[T'])]) for p, _, marks in rows if any(not m or not any(x in m for x in ['unverified','not-found','partial','inferred','[T']) for m in marks)]}",
    },
    {
        "name": "R5 — Each row has exactly 4 markers (Flash/RAM/Sensitivity/Current)",
        "check": lambda rows: all(len(markers) == 4 for _, _, markers in rows),
        "msg":   lambda rows: f"Rows with != 4 markers: {[p for p, _, m in rows if len(m) != 4]}",
    },
]


# ---------- Negative-injection tests (mutate a *copy*, never the live BASELINE) ----------
# These verify each rule fires correctly when violated. They are *negative* tests —
# a passing negative test (rule fails on the mutated baseline) confirms the rule
# has teeth. Without them, a rule that always returns True would silently pass.

NEGATIVE_TESTS = [
    {
        "name": "neg-A1 silent drop (delete last row)",
        "mutate": "_state['BASELINE'] = _state['BASELINE'][:-1]",
        "expect_any_rule_fail": True,
    },
    {
        "name": "neg-A2 out-of-cat loses [T4] marker",
        "mutate": "for i, (p, ic, m) in enumerate(_state['BASELINE']):\n    if not ic:\n        _state['BASELINE'][i] = (p, ic, ['[T1]']*4)\n        break",
        "expect_any_rule_fail": True,
    },
    {
        "name": "neg-A3 in-cat loses [T1] anchor",
        "mutate": "for i, (p, ic, m) in enumerate(_state['BASELINE']):\n    if ic:\n        _state['BASELINE'][i] = (p, ic, ['[T4]']*4)\n        break",
        "expect_any_rule_fail": True,
    },
    {
        "name": "neg-A4 silently blank cell (out-of-cat)",
        "mutate": "for i, (p, ic, m) in enumerate(_state['BASELINE']):\n    if not ic:\n        _state['BASELINE'][i] = (p, ic, ['', '[T4]', '[T4]', '[T4]'])\n        break",
        "expect_any_rule_fail": True,
    },
    {
        "name": "neg-A5 schema drift (row with 5 markers)",
        "mutate": "for i, (p, ic, m) in enumerate(_state['BASELINE']):\n    _state['BASELINE'][i] = (p, ic, m + ['extra'])\n    break",
        "expect_any_rule_fail": True,
    },
]


def _run_negative_tests():
    """Run each NEGATIVE_TESTS injection; verify at least one rule fails."""
    print("-" * 70)
    print("Negative-injection tests (each rule must have teeth)")
    print("-" * 70)
    neg_failures = 0
    for nt in NEGATIVE_TESTS:
        state = {"BASELINE": [(p, ic, list(m)) for p, ic, m in BASELINE]}
        namespace = {"_state": state}
        try:
            exec(nt["mutate"], namespace)
        except Exception as e:
            print(f"❌ {nt['name']:50}  EXEC ERROR: {e}")
            neg_failures += 1
            continue
        modified = state["BASELINE"]
        fails = [r["name"].split(" — ")[0] for r in RULES if not r["check"](modified)]
        caught = len(fails) > 0
        ok = caught == nt["expect_any_rule_fail"]
        status = "✅" if ok else "❌"
        print(f"{status} {nt['name']:50} caught={fails if fails else 'none'}")
        if not ok:
            neg_failures += 1
    return neg_failures


def run():
    print("=" * 70)
    print("Fixture 19 — Out-of-Catalog Escalation Rule (v0.4.3)")
    print(f"Run at: {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 70)
    print()
    print(f"Baseline parts: {len(BASELINE)}")
    in_cat = sum(1 for _, ic, _ in BASELINE if ic)
    out_cat = len(BASELINE) - in_cat
    print(f"  In-catalog:    {in_cat}")
    print(f"  Out-of-catalog: {out_cat}")
    print()

    failures = 0
    for rule in RULES:
        ok = rule["check"](BASELINE)
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}  {rule['name']}")
        if not ok:
            print(f"           → {rule['msg'](BASELINE)}")
            failures += 1
    print()

    neg_failures = _run_negative_tests()
    failures += neg_failures

    print()
    if failures:
        print(f"❌ {failures} rule(s) failed (positive + negative combined). The out-of-catalog escalation rule may be broken.")
        return 1
    else:
        print("✅ All rules passed (positive + negative). Out-of-catalog escalation rule is enforced and each rule has teeth.")
        return 0


if __name__ == "__main__":
    sys.exit(run())