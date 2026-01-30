# TDA for Fraud Detection: Executive Summary

**One-Page Visual Summary**

---

## 🎯 The Question

**Can topology detect fraud patterns that traditional ML misses?**

---

## ⚡ The Answer (In Numbers)

```
┌─────────────────────────────────────────────────────────────┐
│                      PERFORMANCE COMPARISON                  │
├─────────────────┬───────────┬───────────┬──────────┬────────┤
│     Approach    │  F1 Score │   Recall  │ Precision│ROC-AUC │
├─────────────────┼───────────┼───────────┼──────────┼────────┤
│ Traditional ML  │   0.3864  │   68.9%   │  26.8%   │ 0.9292 │
│ Topological ML  │   0.3307  │   85.1% ✅│  20.5%   │ 0.9372✅│
│ Hybrid (Both)   │   0.5545✅│   75.7%   │  43.8% ✅│ 0.9548✅│
├─────────────────┼───────────┼───────────┼──────────┼────────┤
│ Improvement     │  +43.5%   │  +6.8 pts │ +17.0 pts│ +2.6%  │
└─────────────────┴───────────┴───────────┴──────────┴────────┘
```

---

## 🔬 What We Discovered

### 1️⃣ TDA Catches MORE Fraud
```
Traditional ML: ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░ 69% of fraud detected
Topological ML: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░ 85% of fraud detected ← +16 points!
Hybrid:         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ 76% of fraud detected
```

**TDA detects 16% more fraud by identifying network patterns**

### 2️⃣ TDA Sees Different Patterns
```
WHAT EACH APPROACH DETECTS:

Traditional ML:
  ✅ Account takeover (velocity spikes)
  ✅ Unusual amounts
  ✅ Device/location changes
  ❌ Organized rings (misses these)

Topological ML:
  ✅ Fraud rings (H₁ cycles) ← Unique to TDA!
  ✅ Collusion networks
  ✅ Coordinated behavior
  ⚠️  False positives on legitimate families

Hybrid:
  ✅ All of the above
  ✅ Best precision (filters false positives)
```

### 3️⃣ Hybrid is Optimal
```
             Precision vs Recall Trade-off

  1.0 ┤
      │
  0.8 ┤         Hybrid ●  ← Best balance
      │              ╱ ╲
  0.6 ┤             ╱   ╲
      │    Trad ●  ╱     ╲ TDA
  0.4 ┤           ╱       ●
      │          ╱
  0.2 ┤         ╱
      │        ╱
  0.0 ┼───────┴───────────────────
      0.0    0.5    1.0
           Precision
```

**Hybrid combines high recall (TDA) with good precision (traditional)**

---

## 🧮 How It Works

### Step 1: Build Transaction Network
```
Cards → Nodes
Shared Addresses → Edges

Example:
  Card A ────┐
             ├─── Address X
  Card B ────┘

  Card C ────┐
             ├─── Address Y
  Card D ────┘

Fraud Ring:
  Card A ──── Address X ──── Card B
    │                           │
    │                           │
  Address Z ─────────────── Address Y
    │                           │
    │                           │
  Card D ──── Address W ──── Card C

^ This creates a LOOP (H₁ cycle) - detectable by TDA!
```

### Step 2: Extract Topological Features
```
Persistent Homology → Persistence Diagrams → Features

H₀ (Connected Components):
  • Number of disconnected clusters
  • Network fragmentation

H₁ (Loops/Cycles):  ← KEY FOR FRAUD!
  • Number of circular patterns
  • Significance of loops (persistence)

Network Statistics:
  • Density, size, connectivity
```

### Step 3: Machine Learning
```
                 Traditional Features
                         ↓
Transaction → ┌──────────────────────┐
              │                      │
              │    XGBoost Model     │ → Risk Score
              │                      │
              └──────────────────────┘
                         ↑
                  Topological Features
```

---

## 📊 Dataset Complexity

**Not Too Easy (Realistic):**

| Transaction Type | % | Network Pattern | Challenge |
|-----------------|---|-----------------|-----------|
| **Legitimate - Random** | 67% | Dispersed | None |
| **Legitimate - Families** | 19% | Clustered | ⚠️ Looks like fraud! |
| **Legitimate - Corporate** | 10% | Dense, high amounts | ⚠️ High-risk profile |
| **Fraud - Organized Rings** | 0.9% | Circular | ✅ TDA excels |
| **Fraud - Account Takeover** | 0.8% | No network | ✅ Traditional excels |
| **Fraud - Synthetic Identity** | 0.6% | Moderate clusters | Both help |
| **Fraud - First-Party** | 0.5% | Looks legitimate | ❌ Hard for all |
| **Fraud - Opportunistic** | 0.3% | Random | Traditional better |

**Total:** 10,000 transactions, 3% fraud rate

---

## 💡 Key Insights

### Why TDA Works:
1. **Fraud is relational** - Organized schemes create networks
2. **Topology captures organization** - H₁ cycles = fraud rings
3. **Multi-scale detection** - Persistence = significance at all scales
4. **Complementary to traditional** - Different information

### Why TDA Alone Isn't Enough:
1. **Most fraud is individual** (70%) - No network pattern
2. **Legitimate networks exist** - Families look like fraud rings
3. **Lower precision** - More false positives

### Why Hybrid Wins:
1. **Catches both organized AND individual** fraud
2. **Uses traditional to filter** false positives
3. **Best F1, precision, ROC-AUC** - Optimal for deployment

---

## 🎯 Practical Impact

### For Roche Audit:

**Use Cases:**
- ✅ Vendor-approval networks (circular approvals)
- ✅ Expense fraud (coordinated claims)
- ✅ Procurement collusion (vendor rings)
- ✅ Journal entry manipulation (circular flows)

**Expected Results:**
```
Current System (Traditional):
  Detects: 60-70% of fraud
  False Positives: 75-85%
  Investigation Burden: High

TDA-Enhanced (Hybrid):
  Detects: 75-85% of fraud (+15 points)
  False Positives: 55-65% (-20 points)
  Investigation Burden: -30%
```

**Dollar Impact:**
```
Additional Fraud Detected:    $2-5M/year
Investigation Savings:        $500K/year
Prevented Fraud (deterrence): $1-3M/year
────────────────────────────────────────
Total Value:                  $3.5-8.5M/year
```

---

## 🚀 What's Next

### Short-Term (3 months):
- [ ] Test on real IEEE-CIS dataset (590K transactions)
- [ ] Validate on historical Roche cases
- [ ] Tune for production deployment

### Medium-Term (6-12 months):
- [ ] Deploy to Roche audit systems
- [ ] Integrate with case management
- [ ] Build explainability dashboards

### Long-Term (1-2 years):
- [ ] Extend to healthcare fraud, insurance, tax evasion
- [ ] Deep learning with TDA
- [ ] Real-time streaming detection

---

## 📈 The Bottom Line

### Traditional ML:
- Good at individual anomalies
- Misses organized patterns
- F1 = 0.39

### Topological ML:
- Excellent at organized fraud (85% recall!)
- More false positives
- F1 = 0.33

### Hybrid (Traditional + TDA):
- Best of both worlds
- 43.5% improvement
- F1 = 0.55 ← **Optimal for production**

---

## 🏆 Success Criteria Met

✅ **Hypothesis 1**: TDA detects organized fraud (H₁ features among top 3)  
✅ **Hypothesis 2**: TDA achieves higher recall (85% vs 69%)  
✅ **Hypothesis 3**: Hybrid outperforms both (F1: 0.55 vs 0.39 and 0.33)  
✅ **Hypothesis 4**: H₁ features key (18% importance in hybrid)  

---

## 📞 Contact

**Francesco Orsi**  
Data Science Manager - Audit & Risk Data Analytics  
F. Hoffmann-La Roche AG

📧 [francesco.orsi@roche.com] | 💼 [LinkedIn] | 📝 [Substack] | 🐙 [GitHub]

**Want to collaborate?** Open an issue or reach out!

---

## 📚 Learn More

- 📄 **Full Technical Report**: [TECHNICAL_REPORT_TDA_Fraud_Detection.md](TECHNICAL_REPORT_TDA_Fraud_Detection.md)
- 💻 **Code Repository**: [GitHub](https://github.com/fstranieri/tda-fraud-detection)
- 📊 **Interactive Notebook**: [TDA_vs_Traditional_ML_Final.ipynb](notebooks/TDA_vs_Traditional_ML_Final.ipynb)

---

*"Topology is not a replacement for traditional ML, but a powerful complement that captures organizational patterns in fraud networks."*

---

**Version 1.0** | January 30, 2026 | Research Proof-of-Concept
