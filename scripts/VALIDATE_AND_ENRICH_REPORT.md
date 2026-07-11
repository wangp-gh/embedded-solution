# 2026-07-07 validate_and_enrich.py — First Batch Report

## 总览

跑了 `python3 scripts/validate_and_enrich.py --batch` on 125 yaml in `specs/`。

| 类别 | 数量 |
|------|------|
| **Verified (matched all fields)** | ~53 |
| **With not_found (verify gap)** | 36 |
| **Missing critical fields** | 89 |
| **No resolvable PDF** | 36 |

注意 89 个"missing critical fields"多数是 PDF 都对但 yaml 没填字段 — `update_specs.py --dry-run` 然后 enrich 即可填。

## With not_found (Verify Gaps)

详见 `/tmp/enrich_batch.log`，每个 grep "Match.*Not found: [1-9]" 行对应一个 yaml。

特点:
- **多数是 verify 脚本能力不够**,不是数据错 — 比如 `ble_version` "5.0",PDF 里写 "Bluetooth 5 (LE)"。
- **少数是真字段缺失** —— 见下方 Missing critical fields。

## Missing Critical Fields — Top Priority for Enrichment

`(12+ 个 critical field 都没填,扩充潜力最大)`

| Vendor  | Part           | Missing count |
|---------|----------------|--------------:|
| NXP     | K66            | 12 |
| TI      | MSPM0G3507     | 12 |
| GigaDev | GD32E230xx     | 12 |
| GigaDev | GD32F303xx     | 12 |
| GigaDev | GD32F450xx     | 12 |
| Espressif | ESP32         | 12 |
| ... (更多见 enriched 脚本输出) |

## No Resolvable PDF

这些 yaml 的 `source_pdf` 路径指向的 PDF 文件不在 `embedded_dev/<vendor>/datasheet/` 也没有 `datasheets/` 顶层 fallback。

**主要类型:**
- **WCH** CH340C/CH340N/CH343P — 未下载 PDF
- **NXP** K 系列 / i.MX_RT 系列 / S32K — 路径格式不同 (`datasheets/<pn>.pdf` 老路径)
- **Silergy** SY8090 等 — 路径格式不同
- **Espressif** 部分 — 同 NXP,路径过时

**修复方法:** 重新跑 `update_specs.py` 让它按 part 名找新位置,或手动 download + fix source_pdf。

## 推荐下一步

1. **扩充 missing critical fields**:跑 `update_specs.py --batch` + 让 `validate_and_enrich.py --enrich` 写 yaml(标 unverified)。
2. **修复 no-PDF 路径**:要么脚本改 source_pdf 到新位置,要么下载缺失 PDF。
3. **持久化脚本**:把 `validate_and_enrich.py` 加入 CI 或 release 前置校验。
