# Build Procedure — embedded-solution release

This document is **the canonical recipe** for cutting a new release from
`embedded-solution-publish` into this release repo.

---

## Prerequisites

- `embedded-solution-publish` repo at `~/.openclaw/workspace/embedded-solution-publish/`
- `embedded-solution-release` repo at `~/.openclaw/workspace/embedded-solution-release/`
- `tar`, `sha256sum`, `git` available
- Working tree of publish repo clean (`git status` returns empty)

---

## Step-by-step

### 1. Bump version in publish repo

In `embedded-solution-publish/SKILL.md`, change `version:` line:

```yaml
version: 0.6.0
```

Commit:

```bash
cd ~/.openclaw/workspace/embedded-solution-publish
git add SKILL.md
git commit -m "release(v0.6.0): <one-line summary>"
git tag v0.6.0
```

### 2. Write release notes

Create `~/.openclaw/workspace/embedded-solution-publish/RELEASE-v0.6.0.md` following the
structure of existing `RELEASE-v0.4.x.md` / `RELEASE-v0.5.0.md`:

- TL;DR (1 paragraph + 5-7 bullets)
- "What this release adds" (one section per major change)
- "Behavioural compatibility matrix" (table comparing previous minor → new minor)
- "What's NOT in this release" (private cache / spec DB)
- "Validation" (live test results)
- "Commit list" (commit list between previous release and current)
- "Rollback" (recovery procedure)

Commit:

```bash
cd ~/.openclaw/workspace/embedded-solution-publish
git add RELEASE-v0.6.0.md
git commit -m "chore(v0.6.0): <changelog entry>"
```

### 3. Build tarball

```bash
cd /tmp
rm -rf /tmp/release-final
mkdir -p /tmp/release-final/embedded-solution-v0.6.0

cd ~/.openclaw/workspace/embedded-solution-publish
cp SKILL.md README.md RELEASE-v0.6.0.md VERIFICATION.md requirements.txt \
   /tmp/release-final/embedded-solution-v0.6.0/

rsync -a --exclude='.DS_Store' \
  --exclude='*/datasheet/' \
  --exclude='*/datasheet-html/' \
  --exclude='*/firecrawl-snapshots/' \
  references/ /tmp/release-final/embedded-solution-v0.6.0/references/

rsync -a --exclude='.DS_Store' --exclude='.firecrawl_key' --exclude='__pycache__/' \
  scripts/ /tmp/release-final/embedded-solution-v0.6.0/scripts/

cd /tmp/release-final
tar czf /tmp/embedded-solution-v0.6.0.tar.gz embedded-solution-v0.6.0/
sha256sum /tmp/embedded-solution-v0.6.0.tar.gz
```

**Mandatory sanity checks** before proceeding:

```bash
# Cache leak check — must return 0
tar tzf /tmp/embedded-solution-v0.6.0.tar.gz | grep -E "/(datasheet|datasheet-html|firecrawl-snapshots)/" | wc -l

# Entry count check — must be 100-300
tar tzf /tmp/embedded-solution-v0.6.0.tar.gz | wc -l

# Tarball size — should be 100-300 KB after exclusions
ls -lh /tmp/embedded-solution-v0.6.0.tar.gz
```

### 4. Stage in release repo

```bash
cd ~/.openclaw/workspace/embedded-solution-release
mkdir -p releases/v0.6.0
cp /tmp/embedded-solution-v0.6.0.tar.gz releases/v0.6.0/
cp ~/.openclaw/workspace/embedded-solution-publish/RELEASE-v0.6.0.md releases/v0.6.0/
```

### 5. Generate SHA256SUMS.txt

```bash
cd releases/v0.6.0
sha256sum embedded-solution-v0.6.0.tar.gz > SHA256SUMS.txt
cat SHA256SUMS.txt
```

### 6. Write manifest.json

Create `releases/v0.6.0/manifest.json` following the schema of existing `manifest.json`:

- `name`, `version`, `release_date`
- `artifacts.tarball.{filename, size_bytes, sha256, extracted_size_bytes, entry_count}`
- `compatibility.{clawhub_min_version, openclaw_min_version, hermes_compatible, runtime_agnostic}`
- `contents.{skill_md_lines, scripts_count, vendors_covered, application_solutions, chip_count_in_catalogue}`
- `highlights` (5-7 bullets)
- `supersedes` (previous minor)
- `source_commit` (publish repo commit hash)
- `git_tag`

### 7. Update `latest` symlink

```bash
cd ~/.openclaw/workspace/embedded-solution-release
rm -f latest
ln -s releases/v0.6.0 latest
```

### 8. Commit

```bash
cd ~/.openclaw/workspace/embedded-solution-release
git add .
git commit -m "release(v0.6.0): <one-line summary>"
git tag v0.6.0
```

### 9. Distribute

GitHub:

```bash
gh release create v0.6.0 ./releases/v0.6.0/embedded-solution-v0.6.0.tar.gz \
  --title "v0.6.0 — <title>" \
  --notes-file ./releases/v0.6.0/RELEASE-v0.6.0.md \
  --public
```

ClawHub:

```bash
# Extract tarball contents (ClawHub publishes from a directory, not a tarball)
mkdir -p /tmp/clawhub-staging
tar xzf ./releases/v0.6.0/embedded-solution-v0.6.0.tar.gz -C /tmp/clawhub-staging/
clawhub publish /tmp/clawhub-staging/embedded-solution-v0.6.0/
```

### 10. Verify

```bash
# GitHub release visible?
gh release view v0.6.0

# ClawHub listing visible?
clawhub inspect embedded-solution

# Install from ClawHub works in a clean test dir?
mkdir -p /tmp/test-skill-install
clawhub install embedded-solution --dir /tmp/test-skill-install
```

---

## Versioning rules

- **Backward-compatible new features** → bump minor (0.X.0)
- **Behavioural change that breaks catalogue consumers** → bump major (X.0.0)
- **Copy edits, refactors, dependency bumps** → bump patch (0.0.X)
- **Always update `manifest.json`'s `supersedes` field** to point at the previous minor/major
- **Always update `latest` symlink** to point at the most recent release

---

## Common pitfalls

- **`git status` not clean** in publish repo at the time of cutting release → mid-release file drift; `git stash` or commit before proceeding
- **`firecrawl-snapshots/` directory leaked** into tarball → upstream scripts regenerated it; check `.gitignore` is up to date and re-run `tar` excludes
- **Forgotten `latest` symlink update** → ClawHub users see stale `latest` channel; always run step 7
- **SHA256 mismatch** between `SHA256SUMS.txt` and tarball → re-run step 3 (do not paste hash by hand)