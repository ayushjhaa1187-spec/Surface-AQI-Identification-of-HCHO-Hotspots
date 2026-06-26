# Data Directory

Use this directory for local datasets only. Large CPCB, INSAT-3D, Sentinel-5P,
FIRMS and reanalysis files are intentionally ignored by Git.

Recommended layout:

```text
data/
├── raw/          # Original downloaded files
└── processed/    # Collocated daily tables and model-ready arrays
```

Keep source URLs, download dates, spatial extent, variables and preprocessing
steps in metadata files or scripts so outputs remain reproducible.
