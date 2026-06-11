# Task B: Architecture Decisions and Logic

## Component 1: Alignment Method

**Method:** Jaccard Similarity (Token Overlap) combined with Normalized Behavioral Volume.
**Justification:** A deterministic rule engine relying on lexical overlap was chosen to keep the solution lightweight and single-command runnable, avoiding the overhead of heavy embedding models.

**Failure Modes and Limitations:**

1. Metaphorical text: Jaccard relies on exact lexical matches. Metaphors or sarcasm in self-talk compared to literal behavioral logs will result in an alignment score of 0.0.
2. Sparsity: Short text snippets yield naturally low overlap scores. To adjust for this, the alignment threshold for divergence triggers is lowered to 0.1.
3. Normalization boundary: Behavioral volume is normalized against a hardcoded dictionary (`DOMAIN_MAXIMUMS`). Unmapped domains fall back to a default value of 10.0, which may skew volume calculations for outliers.
4. Timestamps: The `timestamp` field in `BehavioralLog` is currently processed as an unvalidated string.

## Component 2: Divergence Type Boundaries

The engine categorizes divergence using these explicit thresholds:

* **Blind Spot:** Bypasses scoring. Triggered if self-talk snippets are < 2 and behavioral logs are >= 3.
* **Aspiration Gap:** Bypasses scoring. Triggered if self-talk snippets are >= 2 and normalized behavioral volume (`b_vol`) is <= 0.05.
* **Overstatement:** Semantic alignment exists (`s_sim` >= 0.1) but action volume is low (`b_vol` < 0.4).
* **Understatement:** Action volume is high (`b_vol` > 0.6) but semantic alignment is nearly absent (`s_sim` < 0.1).
* **Aligned:** If the data passes the sufficiency gates but falls outside the extreme thresholds above, it is classified as ALIGNED to prevent forcing an incorrect divergence label.

## Component 3: Evidence Sufficiency and Abstention

* **Abstention Gate:** If a domain contains < 2 self-talk entries AND < 3 behavioral logs, the system immediately returns INSUFFICIENT_EVIDENCE.
* **Parameter Logic:** The system raises a `ValueError` if the `evaluation_days` parameter is <= 0.
* **Uncertainty Score:** Every output includes a calculated uncertainty score ranging from 0.0 to 1.0. This is based on the inverse of the available evidence against an optimal baseline of 15 total data points.

## Component 4: Output Safety

The system uses Python dataclasses and `Literal` typing for its output schema. The classification field is restricted entirely to the predefined enums. By outputting only strict types and raw floats, the system is prevented from generating medical, diagnostic, or characterological language.