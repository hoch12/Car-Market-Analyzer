# Car Market Analyzer

Car Market Analyzer is a machine learning-powered desktop application that estimates the market price of used cars and predicts their future value depreciation over the next 5 years.

## 📌 Features
- **Real-Time Price Estimation**: Predict current market value based on brand, year, mileage, fuel type, and transmission.
- **Future Value Projection**: Visualizes the estimated depreciation curve for years 2026-2030.
- **Data-Driven**: Trained on a dataset of over **2,200 validated listings** from Czech market portals.
- **Robust Validation**: Automatically checks if the selected car configuration (e.g., Brand + Fuel) actually exists in reality to prevent invalid predictions.
- **User-Friendly GUI**: Simple, clean interface fully localized in **Czech**.

---

## 📂 Project Structure

```
Car-Market-Analyzer/
├── data/                  # Dataset storage
│   ├── raw/               # Scraped unprocessed data
│   └── processed/         # Cleaned data for model training
├── docs/                  # Detailed documentation and design analysis
├── notebooks/             # Jupyter Notebooks for EDA and model training [READ MORE](notebooks/README.md)
├── src/
│   ├── app/
│   │   └── gui_app.py     # Main entry point for the GUI application
│   ├── model/
│   │   ├── inference.py   # Prediction logic and internal API
│   │   └── *.pkl          # Trained model artifacts
│   └── scraper/
│       └── sauto_scraper.py # Web scraping module [READ MORE](src/scraper/README.md)
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 🛠️ Technology Stack

This project was built using the following libraries:

- **`scikit-learn`**: Used to train the Random Forest Regressor for price prediction.
- **`pandas`**: Essential for data manipulation, cleaning, and preprocessing during training and inference.
- **`matplotlib`**: Powers the graph visualization within the GUI to show future price trends.
- **`selenium`**: The core of the scraping engine, handling dynamic web content and infinite scrolling.
- **`tkinter`**: The standard Python GUI library, chosen for its portability and simplicity (no external installation required).
- **`joblib`**: Efficient serialization/deserialization of the trained machine learning model.

---

## 🚀 How to Run

### prerequisites
- Python 3.8 or higher installed.

### 1. Clone the Repository
```bash
git clone https://github.com/hoch12/Car-Market-Analyzer.git
cd Car-Market-Analyzer
```

### 2. Create a Virtual Environment
It is recommended to run this project in an isolated virtual environment.

**MacOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Application Launch
Start the GUI application:
```bash
python src/app/gui_app.py
```
