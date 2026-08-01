# TrustFed 2.0 – Enterprise Privacy-Preserving Healthcare Federated Learning Platform

![TrustFed 2.0 Banner](https://img.shields.io/badge/Platform-TrustFed%202.0-blue?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Flower](https://img.shields.io/badge/Flower_FL-FF6F00?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js 15](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=next.js&logoColor=white)

**TrustFed 2.0** is an enterprise-grade, hackathon-ready healthcare federated learning platform engineered with PyTorch, Flower FL, FastAPI, and Next.js 15. It empowers multiple hospitals (Hospital 1 to 4) to collaboratively train global AI models without ever transmitting raw patient records.

---

## 🏗️ System Workflow

```
Hospital Data Upload
        │
        ▼
Step 1: Privacy Shield Engine (Regex + NER PII Redaction ➔ [REDACTED])
        │
        ▼
Step 2: Data Validation Engine (Schema, Corruptions, Resolution Checks)
        │
        ▼
Step 3: Intelligent Data Classifier (Auto-routing: Image / Tabular / Text)
        │
 ┌──────────────┼──────────────┐
 ▼              ▼              ▼
Step 4: CNN   Step 5: ANN    Step 6: BERT
(Vision)     (Tabular)      (Clinical Text)
 └──────────────┼──────────────┘
                ▼
Step 7: Multimodal Feature Fusion Engine (Cross-Attention ➔ 128-d Unified Representation)
                │
                ▼
Step 8: Local AI Model Training (Data Locality Preserved)
                │
                ▼
Step 9: Federated Learning (Flower Framework - Encrypted Parameter Exchange)
                │
                ▼
Step 10: Trust-Based Aggregation Engine (Z-Score Outlier Detection: Z < -1.5 ➔ Isolation)
                │
                ▼
Step 11: Global Healthcare AI Model (Aggregated Trusted Model Weights)
```

---

## 🔑 Key Core Innovations

### 1. Privacy Shield Engine (`privacy/privacy_shield.py`)
- Multi-layer anonymizer using Regex patterns and Rule-Based NER.
- Automatically redacts: **Patient Name, Aadhaar, PAN, Phone, Email, Address, MRN, Hospital ID, Insurance Number, Doctor Name, DOB, Photos, Barcodes, QR metadata** into `[REDACTED]`.

### 2. Data Validation & Intelligent Data Classifier (`validation/`, `classifier/`)
- Checks image corruption, min resolution (128x128), spreadsheet schemas, and duplicate records.
- Automatically routes images to **CNN**, numerical records to **ANN**, and clinical notes to **BERT**.

### 3. PyTorch Multimodal Architecture (`models/`)
- **CNN Module**: Deep convolutional extractor for Chest X-Rays, MRIs, and CT scans with attention spatial maps.
- **ANN Module**: Multi-layer perceptron for blood pressure, SpO2, sugar, BMI, predicting mortality and disease risk.
- **BERT Module**: Transformer text encoder for clinical notes and summaries.
- **Feature Fusion Engine**: Multi-Head Cross-Attention network merging vision, tabular, and text embeddings into a unified 128-d vector.

### 4. Trust-Based Z-Score Aggregation (`trust/`, `aggregation/`)
Replaces standard FedAvg. Calculates:
- Cosine Similarity & Euclidean Distance
- Gradient Norms & Parameter Variances
- Converts similarities to statistical **Z-Scores**.
- If **$Z < -1.5$**, the update is flagged as suspicious.
- Dynamic Trust Score Rules: Start = 100, Normal = +5, Suspicious = -15. Excludes hospitals with score **$< 40$**.

### 5. Adversarial Attack Simulation (`attack/attack_simulator.py`)
Real-time injectable attacks for hackathon defense demonstration:
- **Gradient Poisoning**
- **Random Noise Injection**
- **Label Flipping**
- **Model Poisoning**
- **Backdoor Attack**
- **Sybil Attack**
- **Data Poisoning**

---

## 🚀 Quick Start Guide

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```
- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

---

### Option 2: Local Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload hospital document (Anonymizes PII, validates, and routes) |
| `POST` | `/privacy/anonymize` | Text PII scrubbing sandbox |
| `POST` | `/train/start` | Trigger a federated learning training round |
| `POST` | `/train/stop` | Pause federated training execution |
| `GET` | `/hospital/status` | Get participating hospital nodes status |
| `GET` | `/trust` | Retrieve dynamic trust scores and Z-scores |
| `GET` | `/metrics` | Get complete dashboard JSON summary |
| `POST` | `/attack/toggle` | Inject adversarial attack into target hospital |
