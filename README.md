# 📦 Supplier Sustainability App

This Streamlit app lets users compare and rank packaging suppliers using sustainability and cost criteria. It uses AHP (Analytic Hierarchy Process) to determine weights and TOPSIS to rank suppliers.

---

## 🚀 Features
- Add suppliers with:
  - Cost, emissions, deforestation risk, recyclability
  - Circularity: reuse & return
- Search and view all suppliers
- Visualize cost vs emissions (bubble chart)
- Rank suppliers using AHP-weighted TOPSIS

---

## 🧪 How to Run (Locally)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/supplier-evaluator.git
cd supplier-evaluator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the app
```bash
streamlit run app.py
```

This will open the app in your browser at [http://localhost:8501](http://localhost:8501)

---

## 🧠 Requirements
```
streamlit
pandas
numpy
matplotlib
```

---

## 🎓 How It Works
- `supplier_data.db` is created automatically when the app is launched
- All calculations happen locally
- Each student/user gets their own database instance

---

## 📦 Optional Enhancements
- Export results (PDF/CSV)
- Upload supplier lists (Excel)
- Connect to online databases
- Add filters, scoring presets, live maps, or external emission factor APIs

---

## 🙌 Credits
Created with ❤️ using Streamlit, Python and common decision-making methods.

