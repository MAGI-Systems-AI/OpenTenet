# Risk Assessment — OpenTenet — a plain-markdown AI-assistant operating workspace (constitution/algorithm/memory) with web/PDF-to-markdown ingest tools, a local Python dashboard, and CI + pre-commit secret scanning, read by multiple AI coding CLIs as operating doctrine at session start.

## 1. Executive Summary

> **Overall grade: B+ · Confidence: High**
> Basis: worst residual = Low-Medium; no residual above Low-Medium; plus because a mitigating control was verified in the system's favor (T1, T2, T3, T4, T5, T6, T7) and remediation is already underway.

Catalog: **ISO/IEC 42001 + NIST AI RMF**. 7 findings — 7 evidenced, 0 asserted, 0 unverifiable; 0 open items.

Compensating controls implemented and tested for all 7 findings from the prior D- assessment. Trust boundary on the ingest path (untrusted-DATA banner + injection screen + constitution rule + gitignored quarantine), SSRF egress guard, dependency pinning + pip-audit, dashboard Host-allowlist + write-token, ingest/dashboard audit logs, and a doctrine integrity manifest. 28 offline tests green; CI enforces dep-audit, doctrine integrity, and the test suite.

## 2. System Characterization

_[supplied by the author — not derivable from the typed model]_

## 3. Framework Coverage

Which **ISO/IEC 42001 + NIST AI RMF** functions/themes the findings reference, derived from their cited control ids:

| Function / Theme | Findings |
| --- | --- |
| A.10 Third parties | T3 |
| A.4 Resources | T3 |
| A.6 Life cycle | T2, T4, T5, T6, T7 |
| A.7 Data | T1, T2 |
| Manage | T6 |
| Map | T3 |
| Measure | T1, T2, T4, T5 |

_Note: this is coverage derived from the findings — which controls are actually implemented is author narrative._

## 4. Threat Scenarios & Risk Matrix

| ID | Scenario | Impact | Likelihood | Residual | Evidence | Controls |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | Indirect prompt injection via ingested web/PDF content | High | Low | Low-Medium | EVIDENCED | A.7.5, A.7.4, MEASURE 2.7 |
| T2 | Persistent memory/doctrine poisoning re-fires every session | High | Very-Low | Low-Medium | EVIDENCED | A.7.5, A.6.2.6, MEASURE 2.7 |
| T3 | Unscanned/unpinned ingest-toolchain dependencies | High | Low | Low-Medium | EVIDENCED | A.10.3, A.4.4, MAP 4.1 |
| T4 | Data exfiltration / SSRF via poisoned AI + outbound fetch | High | Low | Low-Medium | EVIDENCED | A.6.2.6, MEASURE 2.7 |
| T5 | Local dashboard writes unauthenticated to AI doctrine files | Moderate | Very-Low | Low | EVIDENCED | A.6.2.6, MEASURE 2.7 |
| T6 | No audit logging of AI actions or content ingest | Moderate | Low | Low | EVIDENCED | A.6.2.8, MANAGE 4.1 |
| T7 | Credential pre-commit scanner is partial and opt-in | High | Very-Low | Low | EVIDENCED | A.6.2.6 |

## 5. Residual Risk

Worst residual risk: **Low-Medium**. This is what drove the grade (see §1 basis).

## 6. Action Items / Options Roadmap

_[supplied by the author — not derivable from the typed model]_

