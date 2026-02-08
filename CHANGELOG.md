# Changelog

## [0.4.0] - 2026-02-08
### Changed
- **Localization:**
    - Switched entire application (GUI, Config, Model) to **Czech language** for consistency with dataset.
    - Updated `config.json` mappings to use Czech keys (`Benzín`, `Nafta`...).
- **Model Accuracy:**
    - **Retrained Model:** Fixed "Identical Price" issue utilizing new data cleaning pipeline.
    - **Brand Normalization:** Implemented advanced parsing to extract brands from URLs and normalize mixed case (e.g. "bmw" -> "BMW").
    - **Data Recovery:** Recovered ~2000 listings that were previously discarded due to malformed titles.

### Added
- **Robust Error Handling:**
    - Validates user input against reliable `model_metadata.json`.
    - Displays specific error messages (e.g., "Škoda with Diesel not found") instead of crashing.

## [0.3.0] - 2026-02-08
### Added
- **Localization System:**
    - Implemented full English localization for the GUI (Labels, Buttons, Dropdowns).
    - Updated `PricePredictor` to map English inputs ('Petrol', 'Diesel') to internal model columns.
    - Localized all internal code comments and docstrings.

### Changed
- **UI Experience:**
    - Enhanced contrast by changing "CALCULATE" button text to **black**.
    - Optimized window geometry (`800x950`) for MacOS.
    - Standardized typography using `Segoe UI`.

## [0.2.4] - 2026-02-08
### Added
- **Documentation:**
    - Created `docs/documentation.md` covering Design, Analysis, and Implementation.
    - Rewrote `README.md` with comprehensive setup instructions and visual architecture.

## [0.2.3] - 2026-02-08
### Added
- **Architecture Refactoring:**
    - Extracted prediction logic into `src/model/inference.py`.
    - Created `PricePredictor` class for better modularity and testing.
    - Added unit tests in `tests/test_inference.py`.

### Fixed
- **Performance:**
    - Fixed Matplotlib memory leak by moving to the object-oriented `Figure` API.

## [0.2.2] - 2026-02-08
### Fixed
- **Critical Bugs:**
    - Fixed "Identical Price" bug by implementing valid fuel mapping for LPG/CNG.
    - Corrected "off-by-one" error in future value projection (2026-2030).
    - Fixed scientific notation in graph labels (now uses 'k', 'M').

## [0.2.1] - 2026-02-08
### Added
- **Machine Learning Integration:**
    - Developed `notebooks/Car_Price_Prediction.ipynb` for EDA and training.
    - Implemented data cleaning pipeline (parsing years, mileage).
    - Trained Random Forest Regressor and exported artifacts (`car_price_model.pkl`).

## [0.2.0] - 2026-02-08
### Added
- **Web Scraper:**
    - Built `src/scraper/sauto_scraper.py` using Selenium.
    - Implemented infinite scrolling and pagination logic.
    - Added extraction of key features (Year, Mileage, Power, Fuel).
- **Data Collection:**
    - Collected initial dataset of >2000 listings from Sauto.cz.

## [0.1.0] - 2026-02-08
### Added
- **Project Structure:**
    - Initialized Git repository and virtual environment.
    - Set up directory layout (`src/`, `data/`, `tests/`).