# Chronis Assessment: Task B - Behavioral-Narrative Divergence

## Overview

This repository contains the submission for Task B of the Chronis AI/ML Engineer Hiring Assessment. The system implements a deterministic rule engine to measure and categorize the divergence between a user's stated self-talk and their structured behavioral logs.

The architecture prioritizes strict output safety, deterministic boundaries, and explicit evidence-sufficiency gating over complex machine learning infrastructure.

## Project Structure

```text
chronis_assessment/
├── data/
│   └── mock_input.json
├── results/
│   └── worked_examples.json
├── src/
│   ├── schemas.py
│   ├── engine.py
│   └── main.py
├── tests/
│   └── test_engine.py
├── decisions.md
├── requirements.txt
└── README.md
```

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Execute the engine

This command processes the mock input data and generates the formatted results in the `/results` directory.

```bash
python -m src.main
```

### 3. Run the test suite

The pytest suite validates the type boundaries, abstention logic, and parameter guards.

```bash
pytest tests/test_engine.py
```

## System Constraints & Design

* **Output Safety:** Enforced structurally using Python `Literal` types and dataclasses to guarantee the system cannot output characterological or medical judgments.
* **Alignment Method:** Utilizes Jaccard Similarity (token overlap) for semantic comparison, combined with normalized behavioral volume.
* **Sufficiency Gating:** The engine implements hard abstention gates, returning `INSUFFICIENT_EVIDENCE` if data falls below minimum reliable thresholds.

For a comprehensive breakdown of the threshold calculations, divergence typing boundaries, and known failure modes, refer to `decisions.md`.
