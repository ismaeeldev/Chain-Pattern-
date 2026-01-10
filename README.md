# Chain Pattern Analysis System (CPAS) - Milestone 1

This project is a deterministic, offline, desktop analytical system for time-series structural decomposition and pattern analysis.

## Project Structure

The project follows a strict hierarchical structure as defined in the SRS:

```
/cpas
├── app.py                  # Entry point
├── ui/                     # GUI components (Tkinter)
│   ├── __init__.py
│   ├── main_window.py      # Main Dashboard
│   ├── plotting.py         # Matplotlib Embedding
│   └── dialogs.py          # Configuration Dialogs
├── core/                   # Domain Logic
│   ├── __init__.py
│   ├── data_loader.py      # CSV Ingestion & Validation
│   ├── extrema.py          # Peak/Trough Detection
│   ├── widgets.py          # Widget & Chain Logic
│   ├── pattern_mould.py    # Pattern Templates & Validation
│   ├── recurrence.py       # Recurrence Plot Logic
│   └── anchors.py          # Anchor Selection & State
├── algorithms/             # The 15 Mathematical Algorithms
│   ├── __init__.py
│   ├── needleman_wunsch.py
│   ├── smith_waterman.py
│   ├── levenshtein.py
│   ├── kruskal_katona.py
│   ├── aho_corasick.py
│   ├── kmp.py
│   ├── boyer_moore.py
│   ├── de_bruijn.py
│   ├── thue_morse.py
│   ├── burnside.py
│   ├── polya.py
│   ├── palindromic_complexity.py
│   ├── lyndon_factorization.py
│   ├── kasiski.py
│   └── index_of_coincidence.py
├── storage/                # Persistence
│   ├── __init__.py
│   └── db.py               # SQLite + JSON handling
└── models/                 # Data Classes
    ├── __init__.py
    └── structures.py       # Dataclasses for Chains, Patterns
```

## Running the Application

1. Ensure you have Python 3.10+ installed.
2. Install dependencies (NumPy, Pandas, Matplotlib):
   ```bash
   pip install numpy pandas matplotlib
   ```
3. Run the application from the root directory:
   ```bash
   python -m cpas.app
   ```
   OR
   ```bash
   python cpas/app.py
   ```

## Development Rules

- **Offline Only**: No APIs, no cloud.
- **Deterministic**: All outputs must be reproducible.
- **Strict Validation**: Invalid CSVs must be rejected.
