# RegIntel: A Free and Public Data-Driven Python Library for Regulatory Risk Intelligence  

## 🧭 Project Purpose

**RegIntel** (short for “Regulatory Intelligence”) is a fully open-source, transparent Python library designed for:

- 🌍 **Monitoring global drug regulations** (using only freely available data)
- 💊 **Tracking pharmaceutical molecule submissions**
- 📊 **Calculating regulatory & development risks**
- 🧠 **Finding historical analogs using similarity analysis**

Built for **R&D teams, Regulatory Affairs, Pharmacovigilance, Compliance, and Internal Audit**, RegIntel offers a reproducible, version-controlled, and explainable toolkit to:
- Mitigate unexpected regulatory failure
- Analyze regional risk patterns over time
- Anticipate risks based on past molecule precedents
- Serve as a computational audit trail

---

## 💡 Why RegIntel? The Problem It Solves

Pharmaceutical organizations are overwhelmed by regulatory complexity:

- Rules and guidance are evolving rapidly across regions (FDA, EMA, Swissmedic, PMDA, etc.)
- Public knowledge of submissions and failures is fragmented and reactive
- Many regulatory tools today require proprietary data or expensive licenses
- Audit departments lack transparent methods to trace decisions or identify patterns in regulatory failures

RegIntel solves this by:
- Tapping into **only public and free regulatory sources**
- **Structuring global data over time**, per molecule, per authority
- **Scoring and visualizing risk levels** for current and planned submissions
- **Comparing new molecules** against thousands of documented submission paths

---

## 🧩 Core Features

| Module                 | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `RegMonitor`           | Monitors regulatory feeds from global public data portals                  |
| `SubmissionTracker`    | Tracks and parses public submission data from FDA/EMA/EDQM                 |
| `RiskEngine`           | Computes regulatory risk based on historical outcomes & contextual signals |
| `SimilarityMatcher`    | Matches current molecules with historical regulatory cases                 |
| `AuditReporter`        | Intermediate results, data lineage, logs, visual reports                   |

---

## 💼 Use Cases

**For R&D & Regulatory Affairs**
- Track live approval trends by region & therapeutic class
- Query former rejections and match current compound similarity
- Map likely review timelines based on historical case clustering

**For Audit & Risk**
- See molecule pipeline risk exposure with drill-down into vulnerability drivers
- Log all regulatory intelligence operations in a reproducible fashion
- Benchmark R&D pipeline risk against external historical baselines

**For Strategy & Portfolio**
- Understand region-level risks vs. competitors over time
- Position molecules wisely across jurisdictions (e.g. accelerated approval risk delta)
- Explore strongest analogs for benchmarking lifecycle time and attrition

## 1. FDA (United States) Open Data Portals

- **openFDA API**  
  - Covers: drug approvals, labeling, adverse events, recalls, drug establishment data.  
  - Access via: [open.fda.gov](https://open.fda.gov)  
  - Key endpoints: Drugs@FDA, Drug Labeling, NDC Directory, FAERS (Adverse Events), Recall Enforcement  
  - Bulk downloads: Available under openFDA APIs for local offline processing.  
  - Documentation and API examples: [openFDA APIs](https://open.fda.gov/apis/drug/)

- **Drugs@FDA Database**  
  - Bulk data on drug approvals, NDA/ANDA details, application histories.  
  - Download at: [FDA Data Files](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)  

- **FDA Orange Book**  
  - Therapeutic equivalence evaluations for approved drug products.  
  - Online access: [Orange Book](https://www.accessdata.fda.gov/scripts/cder/ob/index.cfm)

- **FDA Purple Book**  
  - Licensed biological products including biosimilars.  
  - Access: [Purple Book](https://purplebook.fda.gov/)

- **FDA Adverse Event Reporting System (FAERS)**  
  - Adverse drug event reports, downloadable quarterly files.  
  - Access: [FAERS Public Dashboard](https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-public-dashboard)  

---

## 2. European Medicines Agency (EMA)

- **European Public Assessment Reports (EPARs)**  
  - Scientific assessments and outcomes of centralized procedure applications.  
  - Access: [EMA EPAR database](https://www.ema.europa.eu/en/medicines)

- **EU Clinical Trials Register**  
  - Registered clinical trials with protocol and outcome info.  
  - Access: [EU Clinical Trials Register](https://www.clinicaltrialsregister.eu)

- **Regulatory Guidelines and Notices**  
  - EMA publishes guidelines, safety updates, and procedural changes openly.  
  - Access via EMA website [Guidelines](https://www.ema.europa.eu/en/human-regulatory/research-development/scientific-guidelines)

---

## 3. German PharmNet.Bund and BfArM

- **PharmNet.Bund**  
  - Since 2025, marketing authorizations for products sold in Germany publicly accessible.  
  - Access: [PharmNet.Bund Portal](https://www.pharmnet-bund.de)

- **BfArM DMIDS & Notifications**  
  - Medical device and drug notification systems, adverse events and recalls.  
  - Access via BfArM website: [BfArM](https://www.bfarm.de/EN/Home/home_node.html)

---

## 4. European Directorate for the Quality of Medicines (EDQM)

- **Pharmeuropa** and **Melclass/Knowledge/Standard Terms**  
  - Official monographs, substance classifications, and certification data.  
  - Access: [EDQM public resources](https://www.edqm.eu/en)

---

## 5. International & Reference Chemical/Drug Databases

- **ChEMBL**  
  - Bioactivity and drug-like molecule data, chemical structures, target info.  
  - Access: [ChEMBL](https://www.ebi.ac.uk/chembl/)

- **DrugCentral**  
  - Regulatory approvals, withdrawn products, pharmacological classification.  
  - Access: [DrugCentral](https://drugcentral.org/)

- **PubChem**  
  - Chemical properties and links to clinical and regulatory references.  
  - Access: [PubChem](https://pubchem.ncbi.nlm.nih.gov/)

- **RepoDB**  
  - Drug repositioning and clinical trial outcome tracking database.  
  - Access: [RepoDB](http://repositioning.ucsf.edu/repodb)

- **SuperDrug2**  
  - Comprehensive dataset on marketed drugs, chemical structure, trade names.  
  - Access: [SuperDrug2](http://chembased.com/superdrug2/)


## 🏗️ Overall Architecture

RegIntel’s design focuses on **modularity, transparency, and reproducibility**, structured into clearly separated components that can evolve independently while allowing easy data flow among them.

### High-level Components

| Component           | Function                                                                                  |
|---------------------|-------------------------------------------------------------------------------------------|
| **Data Ingestion**  | Collects and normalizes public regulatory data (FDA, EMA, EDQM, etc.)                      |
| **Submission Tracking** | Central registry of molecule submissions with metadata and update mechanisms            |
| **Risk Scoring Engine** | Calculates multi-metric risk scores for molecules using historical and contextual data  |
| **Similarity Analysis** | Compares current submissions with historical precursors based on chemical, clinical, and regulatory similarity |
| **Reporting & Audit** | Produces auditable reports, visualizations, and logs with traceability to original data  |

---

## 📦 Key Functional Modules

### 1. **RegMonitor**: Regulatory Data Harvester

- Fetches real-time and batch data from public regulatory feeds via:
  - APIs (e.g., openFDA)
  - Periodic scrapers/parsers for EMA, PharmNet.Bund, EDQM documents
- Normalizes heterogeneous input into a common internal schema (JSON/SQL compatible)
- Maintains versioned snapshots for audit purposes and reproducibility

### 2. **SubmissionTracker**: Molecule Submission Registry

- Ingests and updates global drug submission records including:
  - Molecule identifiers (e.g., INN, internal codes)
  - Submission type (NDA, BLA, ANDA, MAA)
  - Indications, sponsors, geographic regions
  - Submission status, dates, outcomes with links to primary sources
- Enables query and filtering by molecule, therapeutic area, regulatory body, or time window

### 3. **RiskEngine**: Regulatory Risk Estimation

- Utilizes explainable feature sets to quantify risk, including:
  - Regulatory environment volatility (change frequency by region/agency)
  - Chemical/therapeutic novelty and complexity
  - Submission completeness proxies
  - Historical approval delays and rejection rates for similar molecules
- Supports machine learning models (e.g., XGBoost) and rule-based scoring with:
  - Configurable weighting of risk factors
  - Confidence intervals and outlier detection
- Outputs both numeric risk scores and detailed breakdown of contributing factors

### 4. **SimilarityMatcher**: Historical Analog Discovery

- Leverages:
  - Chemical fingerprints (from open databases)
  - Therapeutic class and target profiles
  - Regulatory pathway metadata
  - NLP embeddings of publicly available submission documents and assessment reports
- Implements vector-space similarity searches (using FAISS or scikit-learn)
- Provides ranked lists of historical molecules with commentary on outcomes and timelines

### 5. **AuditReporter**: Compliance-ready Reporting

- Generates:
  - Detailed audit trails linking each data point to source URLs or documents
  - Interactive dashboards with filters for molecules, regions, risk levels
  - Exportable reports (HTML, PDF) supporting regulatory or internal audit needs
- Logs all analysis steps, data version info, and user annotations for full traceability

---

## ⚙️ Technical Highlights

- Core written in Python 3.x, leveraging scientific and data libraries such as `pandas`, `requests`, `scikit-learn`, `xgboost`, `beautifulsoup4`, `spaCy`, and `FAISS`.
- Data storage designed using lightweight SQLite or similar, supporting portability and offline use.
- Modular design with clear public APIs for each component, facilitating customization and extension.
- Emphasis on **explainability**, **auditability**, and **open standards**.
- Designed for containerization (Docker) and workflow automation (Airflow/Prefect compatibles).


## 🔍 Risk Estimation Methodology

The **RiskEngine** module produces robust, interpretable regulatory risk scores by combining statistical analysis, domain knowledge, and machine learning trained exclusively on public data:

### Key Risk Factors Considered

| Factor                        | Description                                                                                   | Source / Data Type               |
|-------------------------------|-----------------------------------------------------------------------------------------------|---------------------------------|
| **Regulatory Environment Volatility** | Frequency and magnitude of recent regulatory changes/warnings in the drug’s region & class   | OpenFDA change logs, EMA updates |
| **Historical Approval Timelines**      | Average and variance of approval/review times for similar molecules & indications           | Drugs@FDA datasets, EPAR records |
| **Outcome Frequencies**                | Proportion of approvals, withdrawals, major label changes historically in the molecule’s class | FDA, EMA, PharmNet.Bund public summaries |
| **Chemical/Indication Complexity**     | Indicators of molecule novelty, multi-target profiles, rare indications synthesized from public databases | ChEMBL, PubChem classifications  |
| **Submission Completeness Proxy**      | Inferred from timing and completeness of publicly available submission metadata               | Submission timestamps, update records |

### Approach

- **Feature Extraction:** Automated extraction of numerical and categorical features from dynamic public datasets.
- **Supervised Learning:** Use of gradient-boosted tree models (`XGBoost`) trained on historical submission outcomes (approved/rejected/withdrawn), leveraging open historic data only.
- **Rule-based Supplement:** Handcrafted domain rules to complement ML models where data is sparse.
- **Explainability:** SHAP (SHapley Additive exPlanations) values or similar tools highlight individual risk factor contributions.
- **Calibration:** Scores normalized between 0 (low risk) and 1 (high risk) for intuitive interpretation.

---

## 🔄 Similarity Matching Methodology

The **SimilarityMatcher** evaluates how closely a new molecule submission aligns with historic cases by:

### Multi-Dimensional Similarity Factors

| Dimension                  | Description                                         | Data & Techniques                       |
|----------------------------|-----------------------------------------------------|---------------------------------------|
| **Chemical Structure**      | Fingerprints and substructure matching of molecule  | Open-source fingerprints (MACCS, ECFP) from ChEMBL, PubChem |
| **Therapeutic Indication**  | Standardized indication codes using open ontologies | MeSH, SNOMED CT standard vocabularies |
| **Regulatory Pathway Type** | NDA, ANDA, accelerated approval, orphan drug status | Extraction from public submission metadata |
| **Submission & Outcome Documents** | NLP embeddings of publicly available assessment reports, labeling changes | Sentence-BERT or similar transformer models on EPARs, PDPs, and FDA labels |
| **Sponsor & Market Info**   | Publicly known sponsor type, country, approval status | Public sponsorship data, marketing authorizations |

### Techniques

- Use of **chemical similarity** metrics (Tanimoto, Dice coefficients) for structure comparison.
- **Textual embeddings and semantic search** on regulatory documents and public submission narratives.
- **Clustering and nearest-neighbor search** (e.g., FAISS) for fast identification of top historical matches.
- Composite scoring that balances chemical, textual, and regulatory metadata similarity.

---

## 📈 Combined Use

- **Risk scores are contextualized by similarity matches**, enabling users to:
  - Benchmark pipeline molecules against historically risky or smooth-path analogs.
  - Gain narrative insights from closest historical regulatory decisions.
  - Detect emerging regulatory risk signals early by comparison to high-risk precedent molecules.

---

## 🔧 How This Advances R&D & Audit Risk Management

- Converts voluminous disparate public information into **actionable, risk-scored intelligence**.
- Enhances decision-making quality for submissions, investment, and compliance by leveraging **interpretable data-driven approaches**.
- Provides clear audit trails with links to all underlying public source data and models—improving transparency and regulatory defensibility.

---

## 📑 Reporting & Audit-Ready Documentation

- **Interactive Dashboards:**  
  Built with lightweight Python tools like `Plotly Dash` or `Streamlit` to explore molecules, risk scores, and historical similarity matches interactively, filtered by region, therapeutic class, or risk thresholds.

- **Automated Report Generation:**  
  Export comprehensive reports in HTML or PDF formats, embedding:  
  - Risk breakdowns  
  - Similarity match summaries  
  - Direct links to original public regulatory documents  
  - Version metadata and audit logs

- **Audit Trail and Traceability:**  
  Every analysis step and data refresh is time-stamped and linked back to original public datasets, ensuring full reproducibility and regulatory compliance readiness.

---

## 🚀 Deployment & Integration

- **Standalone Python Package:**  
  Easy installation via `pip`, requiring only open-source dependencies and no proprietary software.

- **Containerization:**  
  Pre-built Docker containers facilitate deployment in cloud or on-premises environments, enabling scheduled data refreshes and batch analyses.

- **API Layer (Optional):**  
  Expose core RegIntel functions as RESTful endpoints for integration into enterprise R&D dashboards or compliance systems.

- **Extensibility:**  
  Modular code design supports easy addition of new public data sources, alternative risk models, or custom similarity metrics.

---

## 🎯 User Experience and Workflow

- **Data Refresh:**  
  On-demand or scheduled updating of regulatory feeds, triggering automatic re-scoring and report regeneration.

- **Exploratory Analysis:**  
  GUI or Jupyter Notebook interfaces allow users to drill into molecule-specific risk factors and historical analogs.

- **Collaboration:**  
  Share reports and dashboards with stakeholders; annotate risk factors using built-in notes for team audit trails.

- **Transparency:**  
  Open source code and detailed documentation demystify model assumptions and data origins, fostering trust.

---

## 🔗 Summary

With **RegIntel**, teams achieve:

| Benefit                         | Description                                   |
|-------------------------------|-----------------------------------------------|
| Open, free, and public-data based | No proprietary data needed                     |
| Transparent, explainable risk scores | Combine stats, ML, and domain rules             |
| Historical similarity insights | Benchmark and contextualize new molecules        |
| Audit-ready, traceable workflows | Full provenance linking back to source data      |
| Easy to deploy and integrate  | Python package, Docker-ready, API extensible        |

---

***RegIntel*** delivers transparent, data-driven regulatory intelligence—supporting modern, risk-aware pharmaceutical R&D and audit functions with rigor and openness.

---

*End of RegIntel documentation series.*  
Thank you for exploring with us!

```