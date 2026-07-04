# Contributing

This repository **does not accept source contributions**. All source-level work happens in the sibling `embedded-solution-publish` repository, which is private.

If you have found a bug, missing part, or want to suggest a new application-solution:

1. **Bug reports** — file at the `embedded-solution-publish` GitHub repo's issues (private, contact maintainer for access).
2. **Datasheet / catalogue corrections** — file at the `embedded-solution-publish` repo's issues. Maintainer verifies against `vendor URL fetch` and updates the catalogue.
3. **New application solutions** — propose a topic via `embedded-solution-publish` repo's `references/application-solution/<proposed-topic>/solution.md` PR.
4. **ClawHub install / runtime errors** — file at the ClawHub registry under the `embedded-solution` skill.

---

## Release cadence

| Type | Cadence |
|------|---------|
| Major (X.0.0) | Rare; only for SKILL.md semantic breaks |
| Minor (0.X.0) | Roughly monthly; aligns with `embedded-solution-publish` minor commits |
| Patch (0.0.X) | Ad-hoc; for typo / refactor / dependency updates |

---

## Maintainer

`wangp-gh` (per `SKILL.md` `author` field) owns both `embedded-solution-publish` and `embedded-solution-release`.