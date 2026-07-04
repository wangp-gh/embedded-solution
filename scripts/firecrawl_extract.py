#!/usr/bin/env python3
"""firecrawl_extract.py — Tier 3/4 PDF + SPA extraction via Firecrawl.

This is a thin wrapper around the firecrawl-py SDK (and a direct-REST
fallback) that:

- Detects API key availability (FIRECRAWL_API_KEY env var).
- Provides a `scrape_pdf(url, out_path=None)` function for raw PDF
  fetch + markdown conversion.
- Provides an `extract_specs(url, schema, vendor=None)` function for
  JSON-Schema-guided extraction of structured spec fields from any
  URL (PDF or HTML).
- Provides a `crawl_url(url, limit=10, include_paths=None)` function
  that uses Firecrawl /v2/crawl (async task + poll) to crawl multiple
  pages from a starting URL. Useful for vendor sites where the JS-
  rendered product detail pages are not directly scrape-able but
  the family-overview / category-list navigation pages are (e.g.
  silergy.com/list/Buck returns 39KB markdown via crawl, but scrape
  on a single product page returns 404).
- Two modes:
    - **keyed** (default when FIRECRAWL_API_KEY is set): uses the
      firecrawl-py SDK. Supports JSON Schema extraction (extract_specs
      returns structured fields).
    - **keyless** (when no key is set): uses direct REST calls to
      api.firecrawl.dev/v2/scrape. Daily cap of ~5–10 unauthenticated
      credits per IP (per Firecrawl's 2026-06 message). extract_specs
      returns an empty dict + the full markdown (callers must run
      their own regex extractor on the markdown in keyless mode).
- Used by `scripts/update_specs.py` as the preferred Tier 3/4 fetch
  path. See SKILL.md Step 4 and `.planning/v0.4.0-firecrawl-integration.md`
  for the broader v0.4.0 context.

## Usage

    # As a library:
    from firecrawl_extract import scrape_pdf, extract_specs, current_mode
    md = scrape_pdf('https://www.ti.com/lit/ds/symlink/cc2340r5.pdf')
    print(f'running in {current_mode()} mode')

    # As a CLI:
    python3 scripts/firecrawl_extract.py scrape <URL> [--out file.md]
    python3 scripts/firecrawl_extract.py crawl <URL> [--limit N] [--include path1,path2] [--exclude path3] [--max-wait SEC] [--out-dir DIR]
    python3 scripts/firecrawl_extract.py check    # mode + key + credits

## Pricing

- Keyless unauthenticated: ~5–10 free credits/day per IP (capped server-side).
- Authenticated free tier: 1,000 plan credits / month, refreshed on
  the billing-cycle date (see credit-usage endpoint). Plus any bonus
  credits on signup (24 observed in 2026-06 test).
- Standard plan: 1 credit per scrape, +4 for JSON extraction.
  See `.planning/v0.4.0-firecrawl-integration.md` for cost analysis.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal

# Force UTF-8 default encoding on macOS Python 3.9 (which defaults to
# ASCII / latin-1 and crashes on `…` U+2026 or Chinese characters in
# HTTP headers / response bodies). This must happen BEFORE `import
# requests` so urllib3 picks up the new codec at import time.
os.environ.setdefault("LANG", "en_US.UTF-8")
os.environ.setdefault("LC_ALL", "en_US.UTF-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass

import requests

# macOS Python 3.9 caches the default encoding (latin-1) at startup.
# When that encoding is used inside urllib3 / http.client.putheader,
# any non-latin-1 character (e.g. `…` U+2026 in API keys, Chinese chars
# in markdown, Japanese in scraped pages) raises UnicodeEncodeError.
# We monkey-patch putheader to: try the original latin-1 path; if that
# fails for a value, encode that value as UTF-8 with `?`-replacement
# for non-representable chars. Most servers (incl. firecrawl.dev) accept
# UTF-8 in Authorization headers without complaint; this only activates
# when latin-1 would have crashed.
import http.client as _http_client
_original_putheader = _http_client.HTTPConnection.putheader

def _safe_putheader(self, header, *values):
    safe_values = []
    for v in values:
        if isinstance(v, str):
            try:
                v.encode("latin-1")
            except UnicodeEncodeError:
                v = v.encode("utf-8", errors="replace").decode("latin-1", errors="replace")
        safe_values.append(v)
    return _original_putheader(self, header, *safe_values)

_http_client.HTTPConnection.putheader = _safe_putheader

# Lazy import: firecrawl-py may not be installed if the user opts out of
# v0.4.0 features. The wrapper falls back to a clear error in that case
# rather than failing at module import — but only for keyed mode.
# Keyless mode does NOT require firecrawl-py.
def _import_firecrawl():
    try:
        from firecrawl import Firecrawl
        return Firecrawl
    except ImportError as e:
        raise RuntimeError(
            "firecrawl-py is not installed. Run:\n"
            "  python3 -m pip install --user firecrawl-py\n"
            "to enable keyed mode (uses SDK + JSON Schema extraction).\n"
            "Keyless mode works without firecrawl-py but loses JSON Schema support."
        ) from e


# ===== Mode detection =====

Mode = Literal["keyed", "keyless", "unavailable"]


def _load_api_key() -> str | None:
    """Resolve the Firecrawl API key from (in order): env var, sibling
    .firecrawl_key file next to this script. The file route exists
    because shell `…` autocorrect / mangling has been observed to
    pollute the env var on macOS shells (e.g. when echoing the key
    through a chat client). The file is byte-perfect.
    """
    k = os.environ.get("FIRECRAWL_API_KEY")
    if k:
        return k
    key_file = Path(__file__).parent / ".firecrawl_key"
    if key_file.exists():
        try:
            return key_file.read_text(encoding="utf-8").strip() or None
        except Exception:
            return None
    return None


def current_mode() -> Mode:
    """Return the current operating mode.

    - 'keyed': FIRECRAWL_API_KEY is set AND firecrawl-py is importable.
    - 'keyless': no key, but REST endpoint is reachable (we don't
      preflight — keyless is allowed to attempt and report 429 on quota).
    - 'unavailable': no key AND firecrawl-py is missing (would still
      allow keyless, but if both are gone we say unavailable so callers
      don't try).
    """
    has_key = bool(_load_api_key())
    if has_key:
        try:
            _import_firecrawl()
            return "keyed"
        except RuntimeError:
            # Key set but SDK missing — fall through to keyless.
            # Keyless doesn't need the SDK.
            pass
    # No key (or SDK missing despite key) → keyless if requests is available.
    try:
        import requests  # noqa: F401
    except ImportError:
        return "unavailable"
    return "keyless"


def is_available() -> bool:
    """Backwards-compatible availability check.

    Returns True iff either keyed or keyless mode is operational.
    Previously required FIRECRAWL_API_KEY; now also accepts keyless.
    """
    return current_mode() != "unavailable"


# ===== Keyed (SDK) path =====

def _get_client():
    """Construct a firecrawl-py client. Requires FIRECRAWL_API_KEY + SDK.

    Kept for backwards compatibility with callers that already imported it.
    """
    Firecrawl = _import_firecrawl()
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError(
            "FIRECRAWL_API_KEY env var is not set. "
            "Use current_mode() to detect keyless and route accordingly."
        )
    return Firecrawl(api_key=api_key)


def _extract_markdown(result: Any) -> str:
    """Normalize Firecrawl v2 response (SDK or REST) to markdown string."""
    if hasattr(result, "markdown"):
        md = result.markdown
        if md is not None:
            return md
    if isinstance(result, dict):
        return result.get("markdown", "") or ""
    return ""


def _extract_json(result: Any) -> dict[str, Any]:
    """Normalize Firecrawl v2 JSON format response (SDK or REST) to a dict."""
    if hasattr(result, "json"):
        j = result.json
        if j is not None:
            return j
    if isinstance(result, dict):
        return result.get("json", {}) or {}
    return {}


# ===== Keyless (direct REST) path =====

_FIRECRAWL_BASE = "https://api.firecrawl.dev"


def _scrape_via_rest(url: str, formats: list[Any], timeout: int = 60) -> dict[str, Any]:
    """POST /v2/scrape directly. Returns the parsed JSON envelope:
    {"success": bool, "data": {...}} on success, raises on HTTP error.

    On 429 / 402 / 401, raises RuntimeError with the server's message so
    callers can react (keyless daily cap is real).
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    r = requests.post(
        f"{_FIRECRAWL_BASE}/v2/scrape",
        json={"url": url, "formats": formats},
        timeout=timeout,
    )
    if r.status_code == 429:
        raise RuntimeError(
            "Firecrawl keyless daily quota exhausted. "
            "Set FIRECRAWL_API_KEY for 1000 credits/month, or wait for "
            "the daily reset. Server message: " + r.text[:300]
        )
    if r.status_code in (401, 402):
        raise RuntimeError(
            f"Firecrawl auth/billing error ({r.status_code}): {r.text[:300]}"
        )
    r.raise_for_status()
    return r.json()


def get_credit_balance() -> dict[str, Any] | None:
    """Return credit-usage info when a key is configured. None otherwise.

    Tries v2 then v1 credit-usage endpoints. Returns the parsed 'data'
    dict on success (e.g. {remaining_credits, plan_credits,
    billing_period_start, billing_period_end, ...}).
    """
    api_key = _load_api_key()
    if not api_key:
        return None
    # Reconfigure stdout/stderr to UTF-8 to survive macOS Python 3.9's
    # default latin-1 codec (which would crash on `…` / Chinese chars
    # in API keys or markdown). This is a no-op on Linux/Windows where
    # UTF-8 is the default.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    headers = {"Authorization": f"Bearer {api_key}"}
    for path in ("/v2/team/credit-usage", "/v1/team/credit-usage"):
        try:
            r = requests.get(
                f"{_FIRECRAWL_BASE}{path}",
                headers=headers,
                timeout=15,
            )
            if r.status_code == 200:
                j = r.json()
                return j.get("data", j)
        except requests.RequestException:
            continue
    return None


# ===== Public API =====

def scrape_pdf(url: str, *, out_path: str | None = None) -> str:
    """Scrape a PDF or HTML URL and return the markdown content.

    Routes by mode:
    - keyed: firecrawl-py SDK with parsers=['pdf'].
    - keyless: direct REST POST. (Server auto-detects PDF; no parser
      flag needed — format=markdown alone returns PDF text.)

    Args:
        url: Direct URL to a PDF file or an HTML product page.
        out_path: If given, also write the markdown to this file path.

    Returns:
        Markdown text extracted from the URL (layout-preserved).

    Raises:
        RuntimeError: If Firecrawl is unavailable (no SDK + no network).
        requests.HTTPError: On non-2xx REST response other than 429.
    """
    mode = current_mode()
    if mode == "unavailable":
        raise RuntimeError(
            "Firecrawl unavailable: set FIRECRAWL_API_KEY or install requests "
            "(already a hard dep — this should not happen)."
        )
    if mode == "keyed":
        client = _get_client()
        result = client.scrape(url, formats=["markdown"], parsers=["pdf"])
        md = _extract_markdown(result)
    else:  # keyless
        envelope = _scrape_via_rest(url, formats=["markdown"])
        md = _extract_markdown(envelope.get("data", {}))
    if out_path:
        Path(out_path).write_text(md, encoding="utf-8")
    return md


def extract_specs(
    url: str,
    schema: dict[str, Any],
    *,
    vendor: str | None = None,
) -> dict[str, Any]:
    """Scrape a URL and extract structured fields per a JSON Schema.

    Args:
        url: Any URL (PDF datasheet, vendor product page, distributor page, ...).
        schema: JSON Schema dict describing the fields to extract.
            Example: {"type": "object", "properties": {"ble_version": {"type": "string"}, ...}}
        vendor: Optional vendor name (e.g. "Renesas") for logging.

    Returns:
        Dict of extracted fields matching the schema. Missing fields are None.

    Behavior by mode:
    - keyed: uses formats=[{"type":"json","schema":schema}], returns
      structured dict.
    - keyless: JSON Schema extraction is NOT supported by the
      unauthenticated endpoint. Returns {} (empty dict) plus the raw
      markdown is logged to <vendor>_<scrapeId>.md in CWD if vendor
      is set (caller can run their own regex extractor on it).
      Callers must check current_mode() and fall back to regex
      extraction on markdown if keyless.
    """
    mode = current_mode()
    if mode == "unavailable":
        raise RuntimeError("Firecrawl unavailable (no SDK + no keyless path).")
    if mode == "keyed":
        client = _get_client()
        result = client.scrape(
            url,
            formats=[{"type": "json", "schema": schema}],
            parsers=["pdf"],
        )
        extracted = _extract_json(result)
        if vendor:
            print(f"[firecrawl:keyed] {vendor} extract: {len(extracted)} fields from {url[:60]}...")
        return extracted
    else:  # keyless
        envelope = _scrape_via_rest(url, formats=["markdown"])
        data = envelope.get("data", {})
        md = _extract_markdown(data)
        meta = data.get("metadata", {}) if isinstance(data, dict) else {}
        scrape_id = meta.get("scrapeId", "unknown")
        if vendor:
            out_md = f"{vendor}_{scrape_id}.md"
            try:
                Path(out_md).write_text(md, encoding="utf-8")
                print(
                    f"[firecrawl:keyless] {vendor} {url[:60]}... → "
                    f"{len(md)} chars markdown → {out_md} "
                    f"(JSON Schema extraction skipped; run regex on the file)"
                )
            except Exception as e:
                print(f"[firecrawl:keyless] {vendor} markdown dump failed: {e}")
        return {}  # keyless path cannot do schema-guided extraction


# ===== Crawl (multi-page) path =====
#
# Firecrawl /v2/crawl is an async task model:
#   POST /v2/crawl with {url, limit, includePaths?, ...} → returns {id}
#   GET  /v2/crawl/{id} → returns {status, total, completed, data[]}
#
# Used by Gap #3 close-out for vendor sites with JS-rendered product
# pages or family-overview navigation pages (e.g. silergy.com/list/Buck
# which firecrawl /scrape returns empty, but /crawl returns 39KB
# markdown). Crawl also lets us specify includePaths to filter to
# relevant sub-pages only.

import time as _time


def _crawl_via_rest(
    url: str,
    *,
    limit: int = 10,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    poll_interval_s: float = 4.0,
    max_wait_s: float = 120.0,
    timeout_per_poll_s: int = 30,
) -> dict[str, Any]:
    """POST /v2/crawl and poll until completed. Returns the parsed envelope.

    Raises RuntimeError on auth/billing error or non-2xx status.
    """
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError(
            "crawl requires FIRECRAWL_API_KEY (no keyless crawl support)."
        )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {"url": url, "limit": limit}
    if include_paths:
        payload["includePaths"] = include_paths
    if exclude_paths:
        payload["excludePaths"] = exclude_paths
    # Start the crawl
    r = requests.post(
        f"{_FIRECRAWL_BASE}/v2/crawl",
        json=payload,
        headers=headers,
        timeout=30,
    )
    if r.status_code in (401, 402):
        raise RuntimeError(
            f"Firecrawl auth/billing error ({r.status_code}): {r.text[:300]}"
        )
    r.raise_for_status()
    start = r.json()
    crawl_id = start.get("id")
    if not crawl_id:
        raise RuntimeError(f"Firecrawl /v2/crawl returned no id: {start!r}")

    # Poll until completed / failed / timed out
    waited = 0.0
    while waited < max_wait_s:
        _time.sleep(poll_interval_s)
        waited += poll_interval_s
        try:
            r = requests.get(
                f"{_FIRECRAWL_BASE}/v2/crawl/{crawl_id}",
                headers=headers,
                timeout=timeout_per_poll_s,
            )
        except requests.RequestException as e:
            print(f"[crawl] poll error: {e}; continuing")
            continue
        if r.status_code != 200:
            print(f"[crawl] poll HTTP {r.status_code}: {r.text[:200]}")
            continue
        env = r.json()
        status = env.get("status")
        if status == "completed":
            return env
        if status == "failed":
            raise RuntimeError(f"Firecrawl crawl {crawl_id} failed: {env!r}")
    raise RuntimeError(
        f"Firecrawl crawl {crawl_id} did not complete within {max_wait_s}s"
    )


def crawl_url(
    url: str,
    *,
    limit: int = 10,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_wait_s: float = 120.0,
) -> list[dict[str, Any]]:
    """Crawl a URL and return the list of scraped pages (each with
    markdown, metadata, etc.).

    Routes:
    - keyed: REST POST /v2/crawl + poll (works in keyed mode only).
    - keyless: not supported (crawl is async task, requires auth).

    Args:
        url: Starting URL (e.g. https://www.silergy.com/list/Buck).
        limit: Max pages to crawl (Firecrawl caps at 100 by default).
        include_paths: Pathname prefixes to include (e.g. ['/product/']).
        exclude_paths: Pathname prefixes to exclude.
        max_wait_s: How long to poll for completion.

    Returns:
        List of dicts, each with 'markdown', 'metadata.sourceURL',
        'metadata.title', 'metadata.statusCode', etc.

    Raises:
        RuntimeError on auth failure, /v2/crawl failure, or timeout.
    """
    env = _crawl_via_rest(
        url,
        limit=limit,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        max_wait_s=max_wait_s,
    )
    return env.get("data", []) or []


# === CLI ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "check":
        # Diagnostic: mode + key + version + balance
        mode = current_mode()
        print(f"current_mode():        {mode}")
        print(f"FIRECRAWL_API_KEY set: {bool(os.environ.get('FIRECRAWL_API_KEY'))}")
        try:
            Firecrawl = _import_firecrawl()
            print(f"firecrawl-py import:   OK")
            try:
                import importlib.metadata
                v = importlib.metadata.version("firecrawl-py")
                print(f"firecrawl-py version:  {v}")
            except Exception:
                pass
        except RuntimeError as e:
            print(f"firecrawl-py import:   FAILED ({e})")
        if mode == "keyed":
            bal = get_credit_balance()
            if bal:
                print(f"credit balance:        {bal}")
            else:
                print(f"credit balance:        (unable to fetch)")
        elif mode == "keyless":
            print(f"credit balance:        n/a (keyless daily cap ~5–10/IP)")
        print(f"is_available():        {is_available()}")
        sys.exit(0 if is_available() else 2)

    elif cmd == "scrape":
        if len(sys.argv) < 3:
            print("usage: firecrawl_extract.py scrape <URL> [--out file.md]")
            sys.exit(1)
        url = sys.argv[2]
        out = None
        if "--out" in sys.argv:
            out = sys.argv[sys.argv.index("--out") + 1]
        try:
            md = scrape_pdf(url, out_path=out)
            print(f"OK: {len(md)} chars extracted (mode={current_mode()})")
            if out:
                print(f"written to: {out}")
        except Exception as e:
            print(f"FAIL: {type(e).__name__}: {e}")
            sys.exit(1)

    elif cmd == "crawl":
        if len(sys.argv) < 3:
            print("usage: firecrawl_extract.py crawl <URL> [--limit N] "
                  "[--include path1,path2] [--exclude path3] [--max-wait SEC] "
                  "[--out-dir DIR]")
            sys.exit(1)
        url = sys.argv[2]
        limit = 10
        include_paths = None
        exclude_paths = None
        max_wait = 120.0
        out_dir = None
        i = 3
        while i < len(sys.argv):
            a = sys.argv[i]
            if a == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1]); i += 2
            elif a == "--include" and i + 1 < len(sys.argv):
                include_paths = sys.argv[i + 1].split(","); i += 2
            elif a == "--exclude" and i + 1 < len(sys.argv):
                exclude_paths = sys.argv[i + 1].split(","); i += 2
            elif a == "--max-wait" and i + 1 < len(sys.argv):
                max_wait = float(sys.argv[i + 1]); i += 2
            elif a == "--out-dir" and i + 1 < len(sys.argv):
                out_dir = sys.argv[i + 1]; i += 2
            else:
                print(f"unknown arg: {a}"); sys.exit(1)
        try:
            pages = crawl_url(
                url, limit=limit,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                max_wait_s=max_wait,
            )
            print(f"OK: {len(pages)} pages crawled (mode={current_mode()})")
            for p in pages[:5]:
                md_len = len(p.get("markdown", ""))
                src = p.get("metadata", {}).get("sourceURL", "?")
                print(f"  - {md_len:6d} chars  {src}")
            if out_dir:
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                for j, p in enumerate(pages):
                    src = p.get("metadata", {}).get("sourceURL", f"page-{j}")
                    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", src.split("//", 1)[-1])[:80]
                    out_file = Path(out_dir) / f"{slug}.md"
                    out_file.write_text(p.get("markdown", ""), encoding="utf-8")
                print(f"written {len(pages)} files to {out_dir}/")
        except Exception as e:
            print(f"FAIL: {type(e).__name__}: {e}")
            sys.exit(1)

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()