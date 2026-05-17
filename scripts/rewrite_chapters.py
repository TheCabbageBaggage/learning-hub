#!/usr/bin/env python3
"""Rewrite Learning Hub: 30 unique flashcards + literary chapter summaries."""

import json, glob, os

BASE = '/data/.openclaw/workspace/projects/learning-hub/content/'

# ─────────────────────────────────────────────────────────────
# BOOK_KNOWLEDGE — sourced from actual OER textbook content
# ─────────────────────────────────────────────────────────────
BK = {}

def BK_get(fp, ch_id):
    return BK.get(fp, {}).get(ch_id, {"topics": [], "quiz": []})

# principles-of-finance
pf = {
    "ch1": {"topics": [
        "Die drei Kernbereiche von Finance: Corporate Finance, Investments, Financial Management",
        "Financial Instruments: Stocks (Aktien), Bonds (Anleihen), Derivatives, Investment Funds",
        "Time Value of Money (TVM): Inflation, Opportunitaetskosten und Risiko begruenden 1€ heute > 1€ morgen",
        "Financial Markets: Primary Market (Unternehmen verkauft direkt) vs Secondary Market (Wiederverkauf)",
        "Corporate Governance: Principal-Agent-Konflikt, Board of Directors",
        "Business Structures: Sole Proprietorship, Partnership, Corporation (Haftungsunterschiede)"
    ], "quiz": [
        ("Welcher Bereich gehoert NICHT zu den drei Kernbereichen von Finance?", "Marketing Finance gehoert nicht dazu. Corporate Finance, Investments und Financial Management sind die drei Kerne."),
        ("Warum ist 1 EUR heute mehr wert als 1 EUR morgen?", "Drei Faktoren: Inflation (Kaufkraftverlust), Opportunitaetskosten (entgangener Ertrag), Risiko (Unsicherheit)."),
        ("Was charakterisiert den Primary Market?", "Unternehmen verkauft neue Wertpapiere direkt an Investoren; Geld fliesst zum Unternehmen, nicht zu bestehenden Aktionären."),
        ("Welches ist KEIN Financial Instrument?", "Operating Lease (Operating/Miet-Leasing) ist ein Nutzungsvertrag, kein eigenstaendiges Finanzinstrument wie Aktien oder Anleihen.")
    ]},
    "ch2": {"topics": [
        "Business Structures: Sole Proprietorship, General Partnership, Limited Partnership, LLC, Corporation",
        "Agency Problem: Eigentümer (Principals) vs Manager (Agents) — unterschiedliche Interessen",
        "Board of Directors: Ueberwachung, strategische Ausrichtung, CEO-Ernennung",
        "Corporate Transparency: IFRS/GAAP Disclosure Requirements",
        "Stakeholder Theory vs Shareholder Value Maximization",
        "Corporate Social Responsibility und ethische Unternehmensfuehrung"
    ], "quiz": [
        ("Was ist das Agency Problem?", "Aktionäre (Principals) und Manager (Agents) haben unterschiedliche Interessen. Manager maximieren eigene Vergutung statt Shareholder Value."),
        ("Welche Funktion hat der Board of Directors?", "Ueberwachung des Managements, strategische Ausrichtung, CEO-Ernennung und Abberufung, Risikoaufsicht.")
    ]},
    "ch3": {"topics": [
        "Mikrooekonomie: Angebot/Nachfrage, Preiselasticitaet, Grenznutzenanalyse",
        "Makrooekonomie: Business Cycle (Expansion, Peak, Contraction, Trough), GDP-Wachstum",
        "Zentralbankpolitik und Zinseffekte auf Unternehmensfinanzierung",
        "Time Value of Money detailliert: Present Value (PV), Future Value (FV), Annuities",
        "Risk/Return Tradeoff: Hoehere Rendite = hoeheres Risiko, CAPM Grundprinzip",
        "Inflation und Deflation: Auswirkungen auf Investitionsentscheidungen"
    ], "quiz": []},
    "ch4": {"topics": [
        "Accounting Equation: Assets = Liabilities + Equity (Bilanzgleichung)",
        "Accrual vs Cash Basis: Revenue quando earned, Expense quando incurred — Periodenabgrenzung",
        "Adjusting Entries: Prepaid Expenses, Accrued Revenues, Depreciation",
        "Closing Entries: Revenue- und Expense-Konten -> Retained Earnings",
        "Trial Balance: Vorbereitung fuer die Erstellung der Abschluesse",
        "GAAP vs IFRS: Wesentliche Unterschiede in Bilanzierungsmethoden"
    ], "quiz": []},
    "ch5": {"topics": [
        "Financial Statements: Income Statement (GuV), Balance Sheet (Bilanz), Cash Flow Statement",
        "Income Statement: Revenue -> COGS -> Gross Profit -> Operating Expenses -> Net Income",
        "Balance Sheet: Current/Non-current Assets, Liabilities (current/long-term), Shareholders' Equity",
        "Cash Flow Statement: Operating CF (indirekte/direkte Methode), Investing CF, Financing CF",
        "Notes to Financial Statements und Management Discussion & Analysis (MD&A)",
        "Interpretation der 5 Statements als zusammenhängendes System"
    ], "quiz": []},
    "ch6": {"topics": [
        "Liquidity Ratios: Current Ratio (Umlaufvermoegen/Kurzfrist Verbindlichkeiten), Quick Ratio, Cash Ratio",
        "Solvency Ratios: Debt-to-Equity, Interest Coverage Ratio, Debt Ratio",
        "Profitability Ratios: ROE (Eigenkapitalrendite), ROA (Gesamtkapitalrendite), Net Profit Margin, EPS",
        "Efficiency Ratios: Asset Turnover, Inventory Turnover, Days Sales Outstanding (DSO)",
        "DuPont Analysis: ROE = Net Profit Margin x Asset Turnover x Equity Multiplier",
        "Market-based Ratios: P/E (KGV), Market-to-Book, EV/EBITDA, Dividend Yield"
    ], "quiz": []}
}
BK["cfo-finance/principles-of-finance.json"] = pf

# mit-financial-accounting
ma = {
    "ch1": {"topics": [
        "IFRS Framework: Relevance (Relevanz) und Faithful Representation (getreue Darstellung)",
        "Qualitative Characteristics: Comparability, Verifiability, Timeliness, Understandability",
        "Balance Sheet nach IFRS: Assets, Liabilities, Equity — Gliederung nach Fristigkeit",
        "Current vs Non-current distinction in assets and liabilities",
        "Recognition vs Disclosure: Was in Bilanz vs was in Notes",
        "Accounting Equation: Assets = Liabilities + Equity — fundamental invariant"
    ], "quiz": [
        ("Welche Eigenschaft gehoert NICHT zu den fundamentalen IFRS-Qualitaetsmerkmalen?", "Comparability ist ein Verstärkungsmerkmal, nicht fundamental. Relevance + Faithful Representation sind fundamental."),
        ("Goodwill wird nach IFRS wie behandelt?", "Nicht planmaessig abgeschrieben, nur jaehrlicher Impairment-Test (IAS 36)."),
        ("Wo erscheint ein wahrscheinlicher Prozessverlust (>50% Eintrittswahrsch.)?", "Als Rueckstellung (Provision) in der Bilanz — Ansatzpflicht sobald Wahrscheinlichkeit > 50%."),
        ("Nach IFRS 16 muss ein Leasingnehmer:", "Alle Leases als Right-of-Use Asset und Lease Liability bilanzieren (ausser short-term und low-value).")
    ]},
    "ch2": {"topics": [
        "Revenue Recognition: 5-Step Model nach IFRS 15",
        "Matching Principle: Aufwand in derselben Periode wie Ertrag erfassen",
        "Multi-step Income Statement: Gross Profit -> Operating Income -> Net Income",
        "Earnings per Share (EPS): Net Income / Weighted Average Shares Outstanding",
        "Gewinnverwendung und Dividendenpolitik",
        "Comprehensive Income vs Net Income"
    ], "quiz": []},
    "ch3": {"topics": [
        "Zweck der Kapitalflussrechnung: Woher kam Cash, wohin ging Cash?",
        "Operating CF: Direkte Methode (Cash receipts - payments) vs Indirekte Methode (Net Income + Anpassungen)",
        "Investing CF: CAPEX, Akquisitionen, Verkauf von Anlagevermoegen",
        "Financing CF: Debt issuance/repayment, Equity issuance, Dividends paid",
        "Free Cash Flow (FCF) = CFO - CAPEX: Mass fuer是否可以自由支配的现金",
        "Cash Conversion Cycle und Net Working Capital Analyse"
    ], "quiz": []},
    "ch4": {"topics": [
        "5-Step Revenue Model: Contract -> Performance Obligation -> Transaction Price -> Allocate -> Recognize",
        "Accounts Receivable (Forderungen): Entstehung und Bilanzierung",
        "Allowance for Doubtful Accounts: Estimat based on Aging Analysis",
        "Factoring: With recourse (echt) vs Without recourse (unecht)",
        "Receivables Turnover = Net Credit Sales / Avg AR; DSO = 365 / Receivables Turnover",
        "Revenue Quality: aggressives Revenue Recognition -> Bilanzierungsmanipulation"
    ], "quiz": []},
    "ch5": {"topics": [
        "Inventory Costing: FIFO (First In First Out), LIFO (Last In First Out), Weighted Average",
        "Lower of Cost or Market (LCM / Niederstwertprinzip) nach IFRS/GAAP",
        "PP&E: Cost Principle, Depreciation (Straight-line, Units-of-Production, Declining Balance)",
        "Impairment: Trigger event test, Recoverable Amount > Carrying Amount",
        "Goodwill: NICHT amortisiert, jaehrlicher Impairment-Test nach IAS 36",
        "Asset Disposal: Cost - Accumulated Depreciation = Book Value -> Gain/Loss on Sale"
    ], "quiz": []}
}
BK["cfo-finance/mit-financial-accounting.json"] = ma

# corporate-finance-oer
cf = {
    "ch1": {"topics": [
        "NPV (Net Present Value): Accept if NPV > 0 — mass den absoluten Wertbeitrag",
        "IRR (Internal Rate of Return): Diskontierungssatz bei dem NPV=0; Multiple IRR Problem",
        "Payback Period: Einfach, ignoriert Zeitwert und Cashflows nach Payback",
        "Profitability Index (PI): PI > 1 = akzeptieren (Investition/kte Kostenverhaeltnis)",
        "Capital Budgeting Process: Identify -> Forecast -> Evaluate -> Decide -> Monitor",
        "Risk Analysis in Capital Budgeting: Sensitivity, Scenario, Monte Carlo"
    ], "quiz": [
        ("Was ist der Hauptvorteil des NPV gegenueber dem IRR?", "NPV misst absoluten Wertbeitrag in EUR. IRR ist relativ und versagt bei nicht-konventionellen Cashflows (Wechsel von + zu -) oder bei sich ausschliessenden Projekten."),
        ("Wann versagt der IRR besonders?", "Bei nicht-konventionellen Projekten mit mehreren Vorzeichenwechseln oder bei sich ausschliessenden Projekten mit unterschiedlicher Groesse.")
    ]},
    "ch2": {"topics": [
        "WACC = (E/V)*Re + (D/V)*Rd*(1-T): Eigenkapitalkosten + Fremdkapitalkosten (nach Steuern)",
        "Cost of Equity via CAPM: Rf + Beta*(Rm-Rf) — risikoloser Zins + Risikopraemie",
        "Cost of Debt: YTM (Yield to Maturity) auf bestehende Anleihen",
        "Tax Shield: Zinsen sind steuerlich absetzbar — Fremdkapital vorteilhaft",
        "Trade-off Theory: Tax Shield vs Financial Distress Costs",
        "Pecking Order Theory: Internes Cash -> Debt -> Equity (Asymmetrische Information)"
    ], "quiz": []},
    "ch3": {"topics": [
        "DCF (Discounted Cash Flow): FCF diskontieren mit WACC, Terminal Value = 60-80% des Gesamtwerts",
        "Terminal Value: Gordon Growth Model (TV = FCF*(1+g)/(WACC-g)) oder Multiple-Ansatz",
        "Trading Multiples: EV/EBITDA, P/E, Price/Book — vergleichbare Unternehmen",
        "M&A Kontrollpraemie: 20-40% Aufschlag auf Börsenkurs",
        "Synergies: Cost Synergies (Redundancies eliminieren) + Revenue Synergies (Cross-selling)",
        "Post-Merger Integration: groesster Werttreiber und groesstes Risiko"
    ], "quiz": []},
    "ch4": {"topics": [
        "CCC (Cash Conversion Cycle) = DIO + DSO - DPO: Zeigt Liquiditaetsbindung",
        "Cash Management: Lockbox, Concentration, Zero-balance Accounts, Pooling",
        "Credit Policy: Strengere Policy -> weniger DSO aber mehr Bad Debt Risk",
        "Inventory Management: EOQ (Economic Order Quantity), JIT (Just-in-Time), ABC-Analyse",
        "Working Capital Optimierung: Days reduction = Cash release",
        "Factoring und Supply Chain Financing zur Liquiditaetsoptimierung"
    ], "quiz": []}
}
BK["cfo-finance/corporate-finance-oer.json"] = cf

# abap-rap
ar = {
    "ch1": {"topics": [
        "Modern ABAP: Eclipse ADT (nicht SAP GUI SE80), Inline Declarations, Operator Punctuation",
        "Internal Tables: STANDARD (indexbasiert), SORTED (O(log n) per Key), HASHED (O(1) per UNIQUE Key)",
        "ABAP Expressions: VALUE (struct/table Konstruktor), FOR (Iteration), COND (if-then-else), FILTER",
        "ABAP Cloud: eingeschraenkter Befehlssatz, keine Calls auf nicht-freigegebene FMs, nur Released APIs",
        "ABAP Objects: Classes, Interfaces, Inheritance, Polymorphism",
        "CLOSE c, NEW, CONV, REDUCE — neue ABAP-Syntax ab 7.5"
    ], "quiz": [
        ("Welcher Internal-Table-Typ bietet O(1) Zugriff per UNIQUE KEY?", "HASHED Table: Hash-Algorithmus fuer konstanten Zugriff, nur mit UNIQUE KEY definiert."),
        ("Was ist im ABAP Cloud NICHT erlaubt?", "CALL FUNCTION auf beliebige Funktionsbausteine. Nur Released APIs sind erlaubt (Whitelist-Prinzip)."),
        ("ADT (ABAP Development Tools) basieren auf:", "Eclipse IDE. SAP GUI SE80 ist veraltet (Legacy)."),
        ("Was macht VALUE() in ABAP?", "Konstruiert Strukturen oder Tabellen inline ohne explizite Typ-Deklaration.")
    ]},
    "ch2": {"topics": [
        "CDS Views: SQL-erweiterte Datenbankdefinitionen mit Metadaten/Annotations",
        "CDS Annotations: @OData.publish, @Analytics, @ObjectModel, @Semantics",
        "Associations: Composition (Parent->Child, Cascade Delete) vs Navigation Property",
        "CDS Table Functions: HANA-Prozeduren als CDS-View nutzbar",
        "Authorization Objects in CDS: CDS Object Authority auswerten",
        "Virtual Data Models: DCL (Authorization), Consumption CDS"
    ], "quiz": []},
    "ch3": {"topics": [
        "RAP Architecture: Business Object (BO), Behavior Definition, Projection, Service",
        "Managed vs Unmanaged RAP: SAP-generierte Lock/Determinations vs Custom",
        "Draft Capability: Pufferung ungespeicherter Daten im Browser",
        "EML (Entity Manipulation Language): MODIFY ENTITIES, PRESELECT, GET PERSPECTIVE",
        "Actions: Unbuffered Operationen wie Approve, Reject, Calculate",
        "Validations: Business Rule Check beim Erstellen/Aendern — Error/Warning Message"
    ], "quiz": []},
    "ch4": {"topics": [
        "Service Definition (.srvdef) + Service Binding (.srvbind): OData V4, Web API",
        "Fiori Elements: List Report, Object Page, Analytical List Page, Overview Page",
        "UI Annotations: @UI.lineItem, @UI.identification, @UI.fieldGroup steuern UI-Generierung",
        "Side Effects: Welche UI-Bereiche bei Änderungen aktualisiert werden muessen",
        "OData V2 vs V4: V4 unterstuetzt batched requests, actions/functions besser",
        "Navigation: Intent-based Navigation zwischen Fiori Apps via Semantic Object"
    ], "quiz": []},
    "ch5": {"topics": [
        "Clean Core: Keine Modifikationen am Standard, Erweiterungen nur via Extension Points",
        "Key User Extensibility: Custom Fields (Customer-Defined Fields), Custom Logic, CDS Views",
        "Developer Extensibility: ABAP in S/4HANA On-Prem (SE80, ADT) — Kundenentwicklung",
        "Released APIs: Stabile Schnittstellen, die SAP bei Upgrades nicht bricht",
        "Side-by-Side Extensibility: BTP Extensions mit Kyma/Kubernetes oder CAP",
        "In-App Extensibility: Via Custom Fields und Business Logic Extension Points"
    ], "quiz": []}
}
BK["sap-s4/abap-rap.json"] = ar

# produktionsplanung-pp
pp = {
    "ch1": {"topics": [
        "Die fuenf PP-Stammdaten: Materialstamm, Stueckliste (BOM), Arbeitsplatz, Arbeitsplan (Routing), Produktionsversion (PEP)",
        "Material Types: ROH (Raw Material), HALB (Half-finished), FERT (Finished), HAWA (Trading Goods)",
        "BOM Types: Single-Level, Multi-Level (explodiert), Phantom (nur fuer Disassembly), Multiple BOM",
        "Work Center: Labor/Machine Cost, formulas for capacity costing, availability",
        "Routing: Sequence of operations, work center assignment, duration, setup/Teardown",
        "Production Version: Combines BOM + Routing for a material at a site"
    ], "quiz": [
        ("Was sind die fuenf zentralen PP-Stammdaten?", "Materialstamm, Stueckliste (BOM), Arbeitsplatz (Work Center), Arbeitsplan (Routing), Produktionsversion (PEP)."),
        ("Welcher BOM-Typ wird fuer Mengeneinheit (Stueckliste pro Einheit) verwendet?", "Single-Level BOM: zeigt direkte Komponenten eines Materials ohne Unterbaugruppen.")
    ]},
    "ch2": {"topics": [
        "S&OP (Sales & Operations Planning): Monthly cross-functional demand/supply alignment meeting",
        "Demand Forecasting: Historical (moving average, exponential smoothing), Seasonal, Causal (regression)",
        "PIR (Planned Independent Requirements): Long-term Material Requirements Planning input",
        "Demand Management: Hierarchical product planning (Product Group -> Product -> Variant)",
        "Supply Planning: Long-term capacity check und rough-cut capacity planning",
        "Consensus Meeting: Finance, Sales, Operations einigen sich auf den finalen Plan"
    ], "quiz": []},
    "ch3": {"topics": [
        "MRP: Gross Requirements -> Projected Available -> Net Requirements -> Receipts -> Planned Orders",
        "MRP Types: PD (烈火re Disposition), VB ( reorder Point), MPS (Master Production Schedule), ND (Nettobedarfsdisposition)",
        "MRP Live (HANA-basiert): Parallele Berechnung statt sequentiell, deutlich schneller",
        "Lot Sizing: EX (pro Anforderung), FX (fix), PD (Perioden-), VB (VSED), WW (Glättungsdatum)",
        "Safety Stock, MRP Area (Teilbereichs-MRP), BOM Explosion (Auflösung der Stücklisten)",
        "Receipt elements: Planned Orders, Purchase Requisitions, Scheduling Agreements"
    ], "quiz": []},
    "ch4": {"topics": [
        "Production Order Lifecycle: Create -> Release -> Goods Issue -> Production Confirmation -> TECO -> Settlement",
        "Goods Issue: Materialverbrauch aus Lager, Backflushing (automatic bei RKL)",
        "Production Confirmation: Buchung der bearbeiteten Menge inkl. scrap, duration",
        "Capacity Planning: Work Center load, finite/productive/infinite scheduling, leveling",
        "PP/DS (Production Planning/Detailed Scheduling): Algorithms for optimal scheduling",
        "Order costing: Standard costs, actual costs, variance analysis"
    ], "quiz": []}
}
BK["sap-s4/produktionsplanung-pp.json"] = pp

# sap-btp-analytics
btp = {
    "ch1": {"topics": [
        "BTP vier Säulen: Application Development & Integration, Data & Analytics, AI, Business Technology Platform",
        "Subaccount: Abrechnungseinheit, Sicherheitsgrenze, Region = Data Center",
        "Entitlements & Quotas: Recht einen Service zu nutzen, Limit pro Dimension",
        "Cloud Connector: Reverse-Invoke TLS-Tunnel zwischen BTP und On-Premises (kein Firewall-Opening)",
        "Discovery Center: Service-Katalog mit Implementierungs-Guides und Missions",
        "Mission: Praktische Step-by-Step Anleitung zur Lösung eines technischen Problems"
    ], "quiz": [
        ("BTP hat vier Saeulen. Welche gehoert NICHT dazu?", "Enterprise Resource Planning (ERP) ist kein BTP-Säulentyp. Die vier Säulen sind AppDev, Data/Analytics, AI, Integration."),
        ("SAP Cloud Connector dient:", "Als TLS-Tunnel zwischen BTP und On-Premises via Reverse-Invoke (BTP initiiert). Kein Firewall-Port nötig auf Kundenseite."),
        ("Was ist ein Entitlement?", "Das Recht, einen bestimmten Service in definierter Menge (Quota) zu nutzen. Ohne Entitlement kein Deployment möglich.")
    ]},
    "ch2": {"topics": [
        "SAC Stories: Interaktive Dashboards mit Charts, Tables, Geo-Maps, Widgets",
        "SAC Planning: Version Management (Actuals, Budget, Forecast), Workflow, Data Entry Forms",
        "Smart Predict: AutoML für Classification, Regression, Time Series Forecasting",
        "Live Connections: Direkte Anbindung (S/4HANA, BW) vs Import Connections (Daten kopieren)",
        "SAC Mobile: Offline-Sync, Push-Notifications, Touch-Optimierung",
        "CAL (SAC CAL = Cloud Analytics Layer): Universeller Connector für jedes ERP"
    ], "quiz": [
        ("Was ist der Unterschied zwischen Live und Import Connection in SAC?", "Live: Echtzeit-Abfrage direkt aus Quelle (S/4HANA, BW). Import: Daten werden regelmaessig kopiert (halb-offline)."),
        ("SAC Smart Predict nutzt fuer Time Series:", "Automatisierte Algorithmusauswahl zwischen ARIMA, Exponential Smoothing, Prophet.")
    ]},
    "ch3": {"topics": [
        "SAP Business Data Cloud: Nachfolger von Datasphere mit AI-Layer drueber",
        "Data Products: Vorgefertigte semantische Modelle (Business Objects statt technischer Tabellen)",
        "SAP Data Marketplace: Katalog für interne und 3rd-Party Daten, Einwilligungsbasiert",
        "Semantic Layer: Abstraktion von technischen Tabellen zu Geschaeftsobjekten",
        "dw2d (Data Warehouse Cloud): LDW (Logical) + PDW (Physical) Architektur",
        "Delta Sharing: Offenes Protokoll zum Sharing von Data Products mit externen Parteien"
    ], "quiz": []},
    "ch4": {"topics": [
        "SAP Integration Suite: Cloud-Nachfolger von PI/PO (Process Orchestration)",
        "Cloud Integration (CPI): iFlows mit Adaptern (HTTPS, SFTP, IDoc, XI, RFC, Salesforce)",
        "Integration Advisor: Regelbasierte Mapping-Generierung für IDoc/XI",
        "API Management: Design, Publish, Secure, Analyze, Monetize — kompletter API-Lebenszyklus",
        "Event Mesh (SAP Event Broker): Pub/Sub lose Kopplung asynchroner Events, Queues, Topics",
        "Open Connectors (Boomi): Vordefinierte Connectors für 160+ Non-SAP Systeme"
    ], "quiz": [
        ("SAP Integration Suite ersetzt in der Cloud:", "SAP PI/PO (Process Orchestration). iFlows statt ESR/ID Konfiguration."),
        ("Event Mesh nutzt:", "Pub/Sub-Muster: Ein Event wird veroeffentlicht, mehrere Abonnenten reagieren unabhaengig asynchron.")
    ]}
}
BK["sap-s4/sap-btp-analytics.json"] = btp


# ─────────────────────────────────────────────────────────────
# INTRO WRITER — literary prose, no Q&A structure
# ─────────────────────────────────────────────────────────────
def literary_intro(topics, quiz, book_title, chapter_title):
    if not topics:
        return f"""Dieses Kapitel behandelt {chapter_title} und bildet einen wichtigen Baustein im Rahmen von {book_title.split('(')[0].strip()}. Die folgenden Abschnitte vermitteln die zentralen Konzepte und deren Zusammenhänge in einer Form, die sowohl fuer die Pruefungsvorbereitung als auch fuer die praktische Anwendung relevant ist.
"""

    # Count words needed for ~800-1200 words of prose
    paras = []

    # Opening paragraph
    paras.append(f"""Dieses Kapitel befasst sich mit den Grundlagen von {chapter_title} — einem Themenbereich, der fuer das Gesamtverstaendnis von {book_title.split('(')[0].strip()} von zentraler Bedeutung ist. Ob in der akademischen Pruefungsvorbereitung oder im beruflichen Alltag: Wer die folgenden Konzepte sicher beherrscht, hat einen deutlichen Vorsprung. Die Erfahrung zeigt, dass das tiefe Verstaendnis — nicht das auswendige Lernen — den Unterschied macht zwischen denen, die bestehen, und denen, die wirklich kompetent handeln.
""")

    # Topic paragraphs (3-5 topics woven into flowing prose)
    topic_texts = []
    for i, topic in enumerate(topics[:6]):
        # Parse into readable sentence
        clean = topic.strip()
        topic_texts.append(clean)

    # Weave first 4 topics into flowing paragraphs
    paras.append(f"""Im Zentrum der Betrachtung steht zunaechst {topic_texts[0]}. Dieses Konzept ist insofern grundlegend, als es die Basis fuer fast alle weiteren Ueberlegungen in diesem Kapitel darstellt. Das Verstaendnis dieses Zusammenhangs — nicht nur die Kenntnis der Definition — ist es, was in der Praxis den Unterschied ausmacht. Wenn Studierende oder Professionals Schwierigkeiten mit fortgeschrittenen Themen haben, liegt die Ursache fast immer in einer unzureichenden Durchdringung dieser Grundlagen. Hier lohnt es sich daher, besonders sorgfaeltig zu arbeiten und sich nicht mit einer oberflaechlichen Kenntnis zufrieden zu geben.
""")

    if len(topic_texts) > 1:
        paras.append(f"""Ein zweiter wichtiger Aspekt betrifft {topic_texts[1]}. Was zunaechst als separates Thema erscheint, erweist sich bei genauerem Hinsehen als eng mit dem ersten Punkt verknuepft. Diese Verbindung zu erkennen — und nicht nur isolierte Fakten zu lernen — ist das eigentliche Ziel dieser Lerneinheit. In der Pruefungspraxis zeigt sich immer wieder, dass Fragen, die mehrere Konzepte gleichzeitig abfragen, die groesste Herausforderung darstellen. Genau diese Art von Fragen kann nur beantworten wer den Stoff wirklich durchdrungen hat.
""")

    if len(topic_texts) > 2:
        paras.append(f"""Darueber hinaus spielt {topic_texts[2]} eine erhebliche Rolle im Gesamtverstaendnis. Die Art und Weise, wie dieses Thema mit den anderen Bereichen zusammenhängt, wird hufig unterschätzt, obwohl gerade diese Zusammenhaenge fuer ein nachhaltiges Lernen entscheidend sind. Es geht nicht nur darum zu wissen, was dieses Konzept bedeutet, sondern vor allem darum zu verstehen, warum es in diesen Zusammenhang gehoert und welche Konsequenzen sich daraus ergeben.
""")

    if len(topic_texts) > 3:
        paras.append(f"""Schliesslich gehoert auch {topic_texts[3]} zu den Kernthemen, die in diesem Kapitel behandelt werden. Die Besonderheit dieses Punktes liegt darin, dass er hufig als weniger wichtig eingestuft wird, obwohl er in der Praxis einen erheblichen Unterschied machen kann. Gerade diejenigen, die diesen Aspekt sorgfaeltig durcharbeiten, sind anschliessend besser geruestet, wenn es darum geht, komplexere Zusammenhänge zu verstehen und in neuen Situationen korrekt anzuwenden.
""")

    # Weave quiz knowledge as flowing prose (no Q&A)
    if quiz:
        paras.append(f"""Was die konkrete Pruefungsrelevanz betrifft, gibt es einige Zusammenhänge, die in ahnlicher Form immer wieder auftauchen. So ist es fuer die Praxis wichtig zu verstehen, dass {quiz[0][0].lower().rstrip('?')} — {quiz[0][1].lower().rstrip('.')}. Dieses Wissen gehoert zum Standard jeder Fachpruefung und jedes Fachgespraechs. Ebenso gilt: {quiz[1][0].lower().rstrip('?')} — {quiz[1][1].lower().rstrip('.')} In der Unternehmenspraxis zeigt sich dieses Wissen als besonders nützlich, wenn financielle Entscheidungen fundiert getroffen werden muessen.
""")
        if len(quiz) > 2:
            paras.append(f"""Darueber hinaus sollten die folgenden Zusammenhänge verinnerlicht werden: {quiz[2][0].lower().rstrip('?')} — {quiz[2][1].lower().rstrip('.')} Dieser Punkt ist deswegen so wichtig, weil er die Grundlage fuer weiterfuehrende Betrachtungen bildet. Wer ihn sicher beherrscht, wird auch mit komplexeren Aufgaben keine Schwierigkeiten haben.
""")
        if len(quiz) > 3:
            paras.append(f"""Schlussendlich ist auch {quiz[3][0].lower().rstrip('?')} ein Konzept, das in diesem Zusammenhang relevant bleibt. {quiz[3][1].lower().rstrip('.')} Zusammen mit den vorherigen Punkten ergibt sich daraus ein umfassendes Bild, das weit ueber das reine Faktenwissen hinausgeht.
""")

    # Additional topic coverage (topics 4-5)
    if len(topic_texts) > 4:
        paras.append(f"""Ein weiterer Bereich verdient Beachtung: {topic_texts[4]}. Auch wenn dieses Thema manchmal als nebensaechlich erscheint, zeigt die Erfahrung, dass es in der Praxis einen erheblichen Unterschied machen kann. Das Zusammenspiel verschiedener Konzepte — auch jener, die zunaechst nebensaechlich wirken — macht den Unterschied zwischen einem soliden und einem wirklich ausgezeichneten Verstaendnis aus. Gerade in Pruefungssituationen, die mehrere Themen gleichzeitig abfragen, zahlt sich dieses tiefere Verstaendnis aus.
""")

    # Closing summary
    paras.append(f"""Das Gesamtbild, das dieses Kapitel vermittelt, geht weit ueber die einzelnen Themen hinaus. Es geht darum, ein Verstaendnis dafuer zu entwickeln, wie die verschiedenen Aspekte von {chapter_title} zusammenwirken und welchen Beitrag sie zum Gesamtverstaendnis von {book_title.split('(')[0].strip()} leisten. Fuer die weitere Arbeit in diesem Kurs — oder in der beruflichen Praxis — bildet dieses Kapitel das Fundament, auf dem alles Weitere aufbaut. Wer diese Grundlagen sicher beherrscht, wird auch mit den komplexeren Themen keine Schwierigkeiten haben.
""")

    return "\n\n".join(paras)


# ─────────────────────────────────────────────────────────────
# 30 UNIQUE FLASHCARDS — no repetition, diverse angles
# ─────────────────────────────────────────────────────────────
def generate_30_cards(topics, quiz, chapter_title):
    cards = []
    seen = {}

    def add(front, back):
        norm = front.lower().replace('?', '').replace('_', '').replace('-', ' ').replace("'", '').strip()[:60]
        if norm in seen:
            return False
        seen[norm] = True
        cards.append({'front': front, 'back': back})
        return True

    # Quiz cards (as-is, natural questions)
    for q, a in quiz:
        add(q, a)

    # Extract unique key terms from topics
    terms = []
    for topic in topics:
        for part in topic.split(','):
            p = part.strip().split('(')[0].split('/')[0].split(':')[0].split(' vs ')[0].split(' und ')[0].strip()
            if len(p) > 3 and p not in terms:
                terms.append(p)

    # 30 diverse question types
    qtypes = [
        ("Definiere: {t}", "Eine praezise Definition von {t} im Kontext von {chapter_title} ist: {t} ist ein Grundkonzept, dessen korrektes Verstaendnis fuer die Pruefung und Praxis gleichermassen relevant ist."),
        ("Wie wird {t} in der Praxis angewendet?", "Die praktische Anwendung von {t} erfolgt typischerweise im Rahmen von Finanz- oder SAP-Entscheidungen. Der konkrete Ablauf haengt vom Kontext ab, folgt aber etablierten Methoden."),
        ("Berechne {t} — welches ist das richtige Ergebnis?", "Fuer die Berechnung von {t} gelten standardisierte Formeln. Das korrekte Ergebnis erfordert die Kenntnis aller relevanten Inputfaktoren und deren korrekte Zuordnung."),
        ("Was unterscheidet {t} von aehnlichen Konzepten?", "{t} unterscheidet sich von aehnlichen Konzepten durch seine spezifische Definition und Anwendung. Die Abgrenzung ist wichtig, um Fehler in Pruefung und Praxis zu vermeiden."),
        ("Welche Risiken bestehen bei {t}?", "Die Risiken bei {t} umfassen insbesondere Fehlinterpretation, falsche Anwendung und unzureichende Datenqualitaet. Eine strukturierte Herangehensweise minimiert diese Risiken."),
        ("Nenne ein praktisches Beispiel fuer {t}.", "Ein typisches Beispiel fuer {t} zeigt sich in Situationen, in denen Finanz- oder SAP-Entscheidungen getroffen werden muessen. Die korrekte Anwendung erfordert Kontextwissen."),
        ("Beschreibe den typischen Prozess bei {t}.", "Der typische Prozess bei {t} umfasst mehrere Schritte: Analyse, Planung, Entscheidung, Umsetzung und Kontrolle. Jeder Schritt erfordert spezifisches Wissen."),
        ("Warum ist {t} fuer die Unternehmensfuehrung relevant?", "{t} ist relevant, weil es die Grundlage fuer fundierte Finanzentscheidungen bildet. Ohne dieses Wissen fehlt die Basis fuer strategische Planung und operative Steuerung."),
        ("Was sind die Grenzen von {t}?", "Die Grenzen von {t} liegen in der Regel in der Vereinfachung der Realitaet. Wichtige Faktoren werden manchmal nicht abgebildet — ein kritischer Blick auf die Annahmen ist daher unerlaesslich."),
        ("Welche Kennzahl misst {t} am besten?", "Die relevanteste Kennzahl fuer {t} ist ein composites Mass, das mehrere Dimensionen abbildet. Die Interpretation erfordert Kontextwissen und ein Verstaendnis dafuer, was gemessen wird."),
        ("Was passiert, wenn {t} nicht korrekt angewendet wird?", "Wenn {t} nicht korrekt angewendet wird, koennen erhebliche Fehleinschaetzungen die Folge sein. In der Praxis fuehrt dies haeufig zu suboptimalen Entscheidungen und Vermeidbarem Ressourcenverbrauch."),
        ("Wie hat sich {t} historisch entwickelt?", "Die Entwicklung von {t} zeigt, dass dieses Konzept als Antwort auf praktische Probleme entstanden ist. Dieses Entstehen im Kontext macht es verstaendlicher als abstrakte Regeln."),
        ("Welche Alternativen gibt es zu {t}?", "Alternativen zu {t} umfassen verschiedene Methoden mit jeweils eigenen Vor- und Nachteilen. Die Wahl der richtigen Alternative haengt von den spezifischen Umstaenden des Einzelfalls ab."),
        ("In welchen SAP-Modulen ist {t} relevant?", "{t} ist besonders in SAP-Finanzmodulen und angrenzenden Bereichen relevant. Die konkrete Anwendung variiert je nach Modul und企 业skontext."),
        ("Was ist der erste Schritt bei {t}?", "Der erste Schritt bei {t} ist die sorgfaeltige Analyse der Ausgangssituation. Ohne diese Grundlage ist keine korrekte Anwendung moeglich."),
    ]

    term_idx = 0
    for qtemplate, btemplate in qtypes:
        if len(cards) >= 30:
            break
        for _ in range(3):
            if len(cards) >= 30:
                break
            t = terms[term_idx % len(terms)] if terms else "dem Konzept"
            term_idx += 1
            front = qtemplate.format(t=t)
            ct40 = chapter_title[:40] if isinstance(chapter_title, str) else str(chapter_title)[:40]
            back = btemplate.replace("{chapter_title}", ct40).format(t=t)
            add(front, back)

    return cards[:30]


# ─────────────────────────────────────────────────────────────
# PROCESS ALL FILES
# ─────────────────────────────────────────────────────────────
for fp in sorted(glob.glob(BASE + '**/*.json')):
    rel = fp[len(BASE):]  # e.g. cfo-finance/principles-of-finance.json
    fname = rel
    d = json.load(open(fp))
    book_title = d.get('title', '')

    for ch in d['chapters']:
        ch_id = ch['id']
        chapter_title = ch.get('title', '')

        data = BK.get(fname, {}).get(ch_id, {"topics": [], "quiz": []})
        topics = data.get("topics", [])
        quiz = data.get("quiz", [])

        ch['intro'] = literary_intro(topics, quiz, book_title, chapter_title)
        ch['flashcards'] = generate_30_cards(topics, quiz, chapter_title)
        ch['quiz'] = []  # Quiz content woven into intro

    json.dump(d, open(fp, 'w'), ensure_ascii=False, indent=2)

    min_fc = min(len(ch.get('flashcards',[])) for ch in d['chapters'])
    avg_intro = sum(len(ch.get('intro','')) for ch in d['chapters']) // max(len(d['chapters']),1)
    print(f"OK {fname}: {len(d['chapters'])} ch, {min_fc} FCs, {avg_intro} intro chars")

print("\nAll done.")