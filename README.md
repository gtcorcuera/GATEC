# GATEC (Global Assessment of Thermal Efficiency and Consumption)

**GATEC** is a Python-based desktop application designed to calculate and analyze the total efficiency of power plants. It allows users to input various consumption metrics (Extraction, Processing, Transportation) and perform sensitivity analysis on Carbon Capture and Storage (CCS) efficiency.

## Features

- **Efficiency Calculation**: Compute total efficiency and efficiency drops based on fuel type and consumption stages.
- **Sensitivity Analysis**: Visualize how changes in CCS percentage affect overall plant efficiency.
- **Interactive Graphs**: View dynamic charts for Energy Contribution and Sensitivity Analysis.
- **History Tracking**: Automatically saves calculations to a local database for future reference.
- **Comparison Tools**: Compare different scenarios with ease using the history view.

## Prerequisites

Before identifying, ensure you have **Python 3.12** or higher installed on your computer.

1.  **Check Python Version**:
    Open Command Prompt (Windows) or Terminal (Mac/Linux) and type:
    ```bash
    python --version
    ```
    If you see `Python 3.12.x` (or higher), you are ready. If not, download it from [python.org](https://www.python.org/downloads/).

2.  **Git (Optional)**:
    Required if you want to clone the repository directly. Download from [git-scm.com](https://git-scm.com/).

## Installation

### 1. Download the Project
Clone the repository or download the ZIP file and extract it to a folder.
```bash
git clone https://github.com/Start-Ops/GATEC.git
cd GATEC
```

### 2. Install Dependencies
GATEC manages dependencies using `pyproject.toml`. You can install them directly using `pip`.

**Windows**:
```bash
pip install .
```

**Mac/Linux**:
```bash
pip install .
```

*Alternatively, if you prefer using a `requirements.txt` (if provided) or manually:*
```bash
pip install ttkbootstrap matplotlib
```

## Usage

### 1. Run the Application
From the project root folder (where `main.py` is located), run:

```bash
python main.py
```

### 2. How to Use
1.  **Home Screen**: shows your recent calculations history. Click "View results" on any card to see details in current execution.
2.  **New Calculation**: 
    - Click "New Calculation" or "+" button.
    - Select a **Fuel Type** (Coal, Natural Gas, etc.).
    - Enter **Plant Efficiency** (0-100%).
    - (Optional) Toggle "Use predefined values" to auto-fill industry averages.
    - Enter consumption values for Extraction, Processing, and Transportation.
    - Enable **CCS** if desired and set its efficiency items.
    - Click **"Calculate"**.
3.  **Results**:
    - View the calculated **Total Efficiency**.
    - Analyze the **Pie Chart** for energy usage breakdown.
    - Inspect the **Sensitivity Graphs** to see how improving CCS technology could impact your plant.

## License

This project is licensed under the Apache 2.0 License.