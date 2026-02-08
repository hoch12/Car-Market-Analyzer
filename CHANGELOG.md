# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Implementation of the graphical user interface (GUI).
- Integration of the model with the desktop application.

## [0.2.0] - 2026-02-08
### Added
- **Web Scraper Module:**
    - Developed `src/scraper/sauto_scraper.py` using Selenium.
    - Implemented robust logic for pagination, cookie handling, and lazy-loading scrolling.
    - Added `config.json` for external configuration management.
    - Implemented state saving (`scraper_state.json`) to allow pausing and resuming downloads.
- **Data Collection:**
    - Successfully scraped over 2000 unique vehicle records from Sauto.cz.
    - Created dataset structure: `data/raw/` and `data/processed/`.
- **Machine Learning Pipeline:**
    - Created Jupyter Notebook `notebooks/Car_Price_Prediction.ipynb` for data analysis.
    - Implemented data cleaning functions (parsing price, year, mileage from text descriptions).
    - Trained a Random Forest Regressor model with successful evaluation charts.
    - Exported trained artifacts: `car_price_model.pkl` and `model_columns.pkl`.

### Changed
- Updated `.gitignore` to exclude large raw data files and virtual environment artifacts.
- Refactored project structure to separate source code (`src`) from notebooks and data.

## [0.1.0] - 2026-02-08
### Added
- Initial project structure setup based on assignment requirements.
- Git repository initialization.
- Documentation folder for future analysis and design documents.