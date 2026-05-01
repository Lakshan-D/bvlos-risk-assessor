# 🚁 BVLOS Flight Risk Assessment Tool

**Independent evaluation framework for Beyond Visual Line of Sight (BVLOS) drone operations — aligned with the EU-funded [EARHEART project](https://earheart-project.eu) and UK CAA / EASA regulatory frameworks.**

---

## What It Does

This tool provides structured, evidence-based risk assessment for BVLOS drone operations across built environment use cases including infrastructure inspection and urban public safety.

It mirrors the independent evaluation responsibilities of the EU EARHEART project, which trials cloud-based BVLOS drone operations and feeds findings into European regulatory frameworks.

**Key capabilities:**

- Interactive flight path planning on live UK map
- Automated risk scoring across 7 operational risk factors
- EASA SORA-based SAIL level estimation
- Airspace conflict detection against ATZ/CTR no-fly zones
- Regulatory framework analysis (UK CAA, EASA, Network Rail)
- Structured JSON report export for consortium/regulatory submission

---

## Regulatory Frameworks Covered

| Framework | Body |
|---|---|
| UK CAA CAP 722 | Civil Aviation Authority |
| EASA UAS Regulation 2019/947 | European Union Aviation Safety Agency |
| EASA SAIL / SORA Assessment | EASA |
| UK Civil Aviation Act 1982 | UK Parliament |
| Network Rail ORR Requirements | Office of Rail and Road |

---

## Tech Stack

- **App:** Streamlit
- **Mapping:** Folium, streamlit-folium
- **Risk Engine:** Custom SORA-aligned scoring (Python)
- **Data:** Pandas
- **Language:** Python 3.10+

---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/Lakshan-D/bvlos-risk-assessor.git
cd bvlos-risk-assessor
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Project Structure

```
bvlos-risk-assessor/
├── app.py                  # Main Streamlit application
├── requirements.txt
├── utils/
│   ├── risk_engine.py      # SORA-based risk scoring engine
│   ├── airspace.py         # Airspace conflict detection
│   └── report.py           # Report generation utilities
└── reports/                # Generated assessment reports
```

---

## Risk Assessment Methodology

Risk scoring is based on the EASA Specific Operations Risk Assessment (SORA) methodology, covering:

| Risk Factor | Basis |
|---|---|
| Ground Risk (Population Density) | EASA SORA GRC Table |
| Altitude Risk | UK CAA CAP 722 / EASA ARC |
| Meteorological Conditions | EASA AMC RPAS.1309 |
| Operational Range | UK CAA BVLOS Policy |
| Contingency / Emergency Plan | EASA SORA OSO #09 |
| UAS Regulatory Category | EASA 2019/947 |
| Kinetic Energy / Speed | EASA SORA Annex B |

---

## Relevance to EARHEART Project

The [EARHEART](https://earheart-project.eu) EU project trials cloud-based BVLOS drone operations and produces regulatory outputs including a BVLOS White Paper. This tool demonstrates the core independent evaluation capability:

```
Trial flight data → Risk assessment → Regulatory mapping → Policy recommendation
```

Consortium partners include Network Rail and UK CAA.

---

## Author

**Lakshan Divakar**
MSc Electronics & Electrical Engineering, Brunel University London
Research Lab Assistant — LiDAR, Drones, AGV, Sensor Fusion

[GitHub](https://github.com/Lakshan-D) | [LinkedIn](https://linkedin.com/in/lakshan-d) | [Email](mailto:lakshan.d.2108@gmail.com)

---

## License

MIT License — free to use, modify, and share with attribution.
