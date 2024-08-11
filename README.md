
# Radar Gesture Prediction System

## Introduction
This project focuses on the development of a radar-based dynamic gesture recognition system, which can predict and identify gestures in real-time. The system includes modules for data processing, model training, real-time prediction, and validation.

## Project Structure
```
project-root/
│
├── data/                # Directory for storing data files
├── docs/                # Documentation and guides
├── src/                 # Source code directory containing the main logic
│   ├── data_processing.py     # Script for data processing and preparation
│   ├── main.py                # Main script that controls the overall application
│   ├── realtime_predict.py    # Script for real-time gesture prediction
│   ├── train.py               # Script for training the model
│   ├── utils.py               # Utility functions used across the project
│   └── validate.py            # Script for validating the trained model
│
├── tests/              # Directory for storing test scripts and data
├── venv/               # Virtual environment for project dependencies
├── README.md           # Project documentation (this file)
└── requirements.txt    # List of Python dependencies
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Radar_Gesture_Predict.git
cd Radar_Gesture_Predict
```

### 2. Set Up the Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
.env\Scriptsctivate   # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Training the Model
To train the model using the preprocessed data, run:
```bash
python src/train.py
```

### Validating the Model
To validate the model on the test data, run:
```bash
python src/validate.py
```

### Real-Time Gesture Prediction
To start the real-time gesture prediction, run:
```bash
python src/realtime_predict.py
```

## Contributing
Feel free to fork this project, submit issues, or contribute by submitting pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
