# PubMed Scraper
PubMed scraper for keyword search and URL extraction

Created by: Fer Aguirre

---
## Directory Structure
```
┬
├─ .gitignore                  # Customized .gitignore for python projects
├─ LICENSE                     # Project's license
├─ pyproject.toml              # Project dependencies
├─ README.md                   # Top-level README for this project
|
├─ assets                      # Resources for the project
|
├─ data                        # Categorized data files                       
|  ├─ processed                # Cleaned data
|  └─ raw                      # Original data
|
├─ notebooks                   # Jupyter notebooks
|  ├─ 0.0-collect-data.ipynb   # Gathering data
|  ├─ 1.0-process-data.ipynb   # Data processing (fixing column types, data cleansing, etc.)
|  ├─ 2.0-analyze-data.ipynb   # Exploratory data analysis
|  └─ 3.0-visualize-data.ipynb # Data visualization methods
|
├─ outputs                     # Exports generated by notebooks
|  ├─ figures                  # Generated graphics, maps, etc. to be used in reporting
|  └─ tables                   # Generated pivot tables to analyze data
|
┴

```
---

## License

This project is released under [MIT License](/LICENSE).

---

This repository was generated with [cookiecutter](https://github.com/cookiecutter/cookiecutter).