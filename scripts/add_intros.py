#!/usr/bin/env python3
"""Add Wikipedia-style chapter intros in German to three CFO Finance JSON files."""

import json
import sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved: {path}")

# ─── Book 1: Principles of Finance ───────────────────────────────────────────

PRINCIPLES_INTROS = {
    "ch1": (
        "**Finance** ist das Management von Geld und Kapital über Zeit — die grundlegende Wissenschaft hinter "
        "Investitionsentscheidungen, der Finanzierung von Unternehmen und dem Funktionieren von Kapitalmärkten. "
        "Dieses Einführungskapitel legt das Fundament für das gesamte Fach: Es definiert die drei Kernbereiche "
        "*Corporate Finance*, *Investments* und *Financial Markets & Institutions*, erklärt die wichtigsten "
        "*Financial Instruments* wie Aktien, Anleihen und Derivate und führt in das zentrale Konzept des "
        "*Time Value of Money* (TVM) ein.\n\n"
        "## Grundkonzepte\n"
        "- **Time Value of Money:** Ein Euro heute ist mehr wert als ein Euro morgen — aus drei Gründen: "
        "Inflation, Opportunitätskosten und Risiko. Dieses Prinzip durchzieht die gesamte Finanztheorie.\n"
        "- **Financial Instruments:** *Stocks* (Eigenkapital), *Bonds* (Fremdkapital), *Derivatives* "
        "(Futures, Optionen, Swaps) und *Cash Equivalents*.\n"
        "- **Marktstruktur:** Primärmarkt (neue Emissionen, Geld fließt zum Unternehmen) vs. Sekundärmarkt "
        "(Handel zwischen Investoren an der Börse).\n\n"
        "## Warum es relevant ist\n"
        "Finance ist weit mehr als Buchhaltung. Ein CFO muss Kapital beschaffen, Investitionen bewerten, "
        "Risiken managen und das *Working Capital* steuern — alles basierend auf den Fundamenten "
        "dieses Kapitels."
    ),
    "ch2": (
        "**Corporate Governance** beschreibt die Regeln, Prozesse und Strukturen, nach denen ein Unternehmen "
        "geführt und kontrolliert wird. In einer Welt getrennter Eigentums- und Kontrollrechte — "
        "*Shareholders* als Eigentümer, *Management* als Lenker — stellt sich die zentrale Frage: "
        "Wie stellt man sicher, dass Manager im Interesse der Aktionäre handeln?\n\n"
        "## Zentrale Konzepte\n"
        "- **Agency Problem (Principal-Agent-Konflikt):** Manager (Agents) können eigene Interessen "
        "(Bonus, Prestige, Größe) über die der Eigentümer (Principals) stellen. Lösungen: "
        "Aufsichtsrat, aktienbasierte Vergütung, Transparenzpflichten.\n"
        "- **Board of Directors:** Drei Rollen — *Monitoring* (Überwachung des CEO), "
        "*Advisory* (strategische Beratung) und *Governance* (Regelsetzung und Compliance).\n"
        "- **Business Structures:** Von der *Sole Proprietorship* (Vollhaftung) über die "
        "*Partnership* bis zur *Corporation* (beschränkte Haftung, Kapitalmarktzugang).\n\n"
        "## Warum es relevant ist\n"
        "ESG-Kriterien (*Environmental, Social, Governance*) gewinnen rasant an Bedeutung. "
        "Der Stakeholder-Ansatz (Wertschöpfung für alle Anspruchsgruppen) löst zunehmend "
        "den reinen *Shareholder-Value*-Fokus ab — mit direkten Auswirkungen auf "
        "Investitionsentscheidungen, Berichtspflichten und den Unternehmenswert."
    ),
    "ch3": (
        "**Ökonomische Grundlagen** bilden das Fundament für jede fundierte Finanzentscheidung. "
        "Dieses Kapitel verbindet mikro- und makroökonomische Konzepte mit der Praxis des "
        "Finanzmanagements — von Angebot und Nachfrage über den Konjunkturzyklus bis zu "
        "Wechselkursen und der Zinskurve.\n\n"
        "## Zentrale Konzepte\n"
        "- **Mikroökonomie:** *Supply & Demand*, *Elasticity*, *Marginal Analysis* und "
        "*Market Structures* bestimmen die Preissetzungsmacht und Margen eines Unternehmens.\n"
        "- **Makroökonomie:** *GDP* (Wirtschaftswachstum), *Inflation* (CPI/PPI) und "
        "*Unemployment* sind die zentralen Inputs für CFO-Planung und Szenarioanalysen.\n"
        "- **Yield Curve (Zinskurve):** Die Differenz zwischen kurz- und langfristigen Zinsen "
        "gilt als einer der zuverlässigsten Rezessionsindikatoren — eine *Inverted Yield Curve* "
        "war Vorbote der letzten sechs US-Rezessionen.\n\n"
        "## Warum es relevant ist\n"
        "Ein CFO muss makroökonomische Signale lesen und antizyklisch handeln können: "
        "Cash-Reserven im Boom aufbauen, in der Rezession strategisch investieren und "
        "Währungsrisiken (*FX Exposure*) aktiv hedgen."
    ),
    "ch4": (
        "Der **Accrual-Accounting-Prozess** ist das methodische Rückgrat der "
        "Finanzbuchhaltung nach IFRS. Anders als die einfache *Cash-Basis* (Einnahmen-Überschuss-Rechnung) "
        "werden Erträge und Aufwendungen bei wirtschaftlicher Entstehung erfasst — unabhängig vom "
        "tatsächlichen Zahlungszeitpunkt. Dieses Kapitel führt durch den gesamten "
        "*Accounting Cycle*.\n\n"
        "## Zentrale Konzepte\n"
        "- **Accounting Equation:** *Assets = Liabilities + Equity* — die Bilanzgleichung, "
        "die jede Buchung im *Double-Entry*-System in Balance hält.\n"
        "- **Accrual vs. Cash-Basis:** Die Periodenabgrenzung nach IFRS sorgt für ein "
        "wirtschaftlich korrektes Bild, während die *Cash-Basis* nur Zahlungsströme zeigt.\n"
        "- **Adjusting Entries:** Vier Kategorien periodengerechter Korrekturbuchungen — "
        "*Accruals* (Zinsabgrenzungen), *Deferrals* (transitorische Posten), "
        "*Depreciation* (Abschreibungen) und *Bad Debt* (Wertberichtigungen).\n\n"
        "## Warum es relevant ist\n"
        "Der Accounting Cycle — von der Analyse des Geschäftsvorfalls über *Journal Entries*, "
        "*Trial Balance*, *Adjusting Entries* bis zu *Financial Statements* und *Closing Entries* — "
        "ist das Standardverfahren jeder Finanzabteilung. Wer diesen Prozess versteht, "
        "versteht, wie Zahlen entstehen — und wie man sie interpretiert."
    ),
    "ch5": (
        "**Financial Statements** sind die Sprache der Unternehmenskommunikation. "
        "Dieses Kapitel lehrt das Lesen und Interpretieren der fünf zentralen "
        "IFRS-Abschlussbestandteile: Bilanz, Gewinn- und Verlustrechnung (GuV), "
        "Kapitalflussrechnung, Eigenkapitalspiegel und Anhang.\n\n"
        "## Zentrale Konzepte\n"
        "- **Balance Sheet (Bilanz):** Zeigt Vermögen (*Assets*), Schulden (*Liabilities*) "
        "und Eigenkapital (*Equity*) zu einem Stichtag — gegliedert nach Fristigkeit.\n"
        "- **Income Statement (GuV):** Von *Revenue* über *EBIT* bis *Net Income* — "
        "die vertikale Struktur der operativen und außerordentlichen Ergebnisse.\n"
        "- **Cash Flow Statement:** Die drei *Cash Flow*-Komponenten — *Operating* "
        "(Tagesgeschäft), *Investing* (Anlageinvestitionen) und *Financing* (Kapitaltransaktionen).\n"
        "- **Common-Size Statements:** Prozentdarstellung aller Posten (% vom Umsatz "
        "oder der Bilanzsumme) für den Vergleich zwischen Unternehmen unterschiedlicher Größe.\n\n"
        "## Warum es relevant ist\n"
        "Nur wer Jahresabschlüsse lesen kann, kann die finanzielle Gesundheit eines "
        "Unternehmens beurteilen, Investitionsentscheidungen treffen oder in "
        "Kreditverhandlungen bestehen."
    ),
    "ch6": (
        "**Finanzkennzahlen** (*Financial Ratios*) verdichten Hunderte von Bilanz- und "
        "GuV-Posten zu aussagekräftigen Metriken. Dieses Kapitel führt in die vier "
        "Hauptkategorien der Kennzahlenanalyse ein — von der Liquidität über "
        "Profitabilität und Verschuldung bis zur Effizienz.\n\n"
        "## Zentrale Konzepte\n"
        "- **Liquidity Ratios:** *Current Ratio* und *Quick Ratio* (Acid Test) messen, "
        "ob ein Unternehmen kurzfristige Verbindlichkeiten bedienen kann.\n"
        "- **DuPont-Analyse:** Zerlegt die Eigenkapitalrendite (*ROE*) in drei "
        "Komponenten — *Net Margin*, *Asset Turnover* und *Equity Multiplier* — "
        "und zeigt, WO die Rendite entsteht.\n"
        "- **Interest Coverage Ratio:** EBIT geteilt durch Zinsaufwand. Werte unter "
        "1,5 signalisieren finanziellen Stress, unter 1,0 Existenzgefahr.\n"
        "- **Cash Conversion Cycle (CCC):** *DIO + DSO − DPO* — die Kapitalbindungsdauer. "
        "Ein negativer CCC (wie bei Amazon) bedeutet kostenlose Finanzierung durch "
        "Lieferanten.\n\n"
        "## Warum es relevant ist\n"
        "Zahlen allein sagen wenig — erst Kennzahlen machen sie vergleichbar und "
        "interpretierbar. Der CFO muss verstehen, welche Kennzahl welches "
        "Geschäftsrisiko abbildet."
    ),
}

# ─── Book 2: MIT Financial Accounting ────────────────────────────────────────

MIT_INTROS = {
    "ch1": (
        "Das **Framework der Rechnungslegung** nach IFRS bildet das konzeptionelle Fundament "
        "für die Erstellung und Interpretation von Jahresabschlüssen. Dieses Kapitel beginnt "
        "mit den qualitativen Anforderungen an *Financial Statements* — *Relevance* und "
        "*Faithful Representation* als fundamentale Merkmale — und führt in den Aufbau "
        "der **Bilanz** (*Balance Sheet*) ein.\n\n"
        "## Zentrale Konzepte\n"
        "- **Recognition vs. Disclosure:** Ein Posten wird entweder in der Bilanz angesetzt "
        "(*Recognition*, mit Zahlenwert) oder nur im Anhang erläutert (*Disclosure*). "
        "Die Grenze bestimmt der Wahrscheinlichkeitsgrad.\n"
        "- **Goodwill:** Entsteht nur bei Unternehmenskäufen als Differenz zwischen Kaufpreis "
        "und *Fair Value* des Nettovermögens. Nach IFRS keine planmäßige Abschreibung, "
        "aber jährlicher *Impairment-Test*.\n"
        "- **IFRS 16 (Leasing):** Seit 2019 bilanzieren Leasingnehmer alle wesentlichen "
        "Leasingverhältnisse als *Right-of-Use Asset* mit entsprechender "
        "*Lease Liability* — die Ära der außerbilanziellen Operating Leases ist vorbei.\n\n"
        "## Warum es relevant ist\n"
        "Ein CFO muss das IFRS-Framework nicht nur anwenden, sondern auch seine "
        "Ermessensspielräume verstehen — um Bilanzpolitik zu erkennen und zu entscheiden, "
        "wie die eigene Bilanz gestaltet wird."
    ),
    "ch2": (
        "Die **Gewinn- und Verlustrechnung** (GuV, *Income Statement*) zeigt den Erfolg "
        "einer Periode — unabhängig von Zahlungszeitpunkten. Das Herzstück dieses "
        "Kapitels ist das *Revenue Recognition Principle* nach IFRS 15 und das "
        "*Matching Principle*, das Aufwendungen und Erträge periodengerecht "
        "einander zuordnet.\n\n"
        "## Zentrale Konzepte\n"
        "- **IFRS 15 (Fünf-Schritte-Modell):** Vertrag identifizieren, "
        "*Performance Obligations* bestimmen, Transaktionspreis ermitteln, Preis "
        "zuordnen, Umsatz bei Erfüllung erfassen — das neue Standardmodell für "
        "Umsatzrealisierung.\n"
        "- **Matching Principle:** Aufwendungen werden in jener Periode erfasst, "
        "in der die zugehörigen Erträge realisiert werden — die Grundlage des "
        "*Accrual Accounting*.\n"
        "- **Revenue vs. Gains:** *Revenue* ist nachhaltig und wiederkehrend "
        "(Kerngeschäft), *Gains* sind einmalig (Asset-Verkäufe). Die Trennung "
        "ist entscheidend für die Prognose nachhaltiger Erträge.\n\n"
        "## Warum es relevant ist\n"
        "*Earnings Management* — die legale oder grenzwertige Nutzung von "
        "Ermessensspielräumen — ist eine der größten Fallen bei der Analyse "
        "von Gewinn- und Verlustrechnungen. Methoden wie *Cookie Jar Reserves*, "
        "*Big Bath* oder *Channel Stuffing* können den wahren Geschäftserfolg "
        "verschleiern."
    ),
    "ch3": (
        "Die **Kapitalflussrechnung** (*Statement of Cash Flows*) beantwortet "
        "die vielleicht wichtigste Frage der Finanzanalyse: Wo kommt das Geld her "
        "und wohin fließt es — unabhängig von buchhalterischen Periodenabgrenzungen? "
        "Während die GuV zeigt, ob ein Unternehmen *wirtschaftlich* erfolgreich ist, "
        "zeigt der *Cash Flow*, ob es *tatsächlich* Geld verdient.\n\n"
        "## Zentrale Konzepte\n"
        "- **Drei Bereiche:** *Operating Cash Flow* (Tagesgeschäft), "
        "*Investing Cash Flow* (Anlageinvestitionen), "
        "*Financing Cash Flow* (Kapitaltransaktionen).\n"
        "- **Direkte vs. Indirekte Methode:** Direkt zeigt jede Ein- und Auszahlung "
        "einzeln. Indirekt startet mit *Net Income* und rechnet nicht-zahlungswirksame "
        "Posten (Abschreibungen, Working-Capital-Veränderungen) zurück. "
        "99% der Unternehmen nutzen die indirekte Methode.\n"
        "- **Free Cash Flow (FCF):** *Operating Cash Flow − CapEx*. Der FCF zeigt, "
        "wie viel frei verfügbares Cash ein Unternehmen nach allen notwendigen "
        "Investitionen generiert.\n\n"
        "## Warum es relevant ist\n"
        "Net Income kann hoch sein, während der *Operating Cash Flow* negativ ist — "
        "etwa bei starkem Umsatzwachstum mit langen Zahlungszielen. "
        "Die Kapitalflussrechnung entlarvt solche Scheingewinne und ist "
        "daher das wichtigste Instrument der Kreditanalyse."
    ),
    "ch4": (
        "**Revenue Recognition** und das Management von **Forderungen** (*Receivables*) "
        "sind zwei der ermessensintensivsten Bereiche der Rechnungslegung. "
        "Wann genau wird Umsatz realisiert? Wie schätzt man das Ausfallrisiko? "
        "Und welche Instrumente gibt es, um Liquidität aus Forderungen zu schöpfen?\n\n"
        "## Zentrale Konzepte\n"
        "- **Allowance for Doubtful Accounts (Wertberichtigung):** Erwartete "
        "Forderungsausfälle werden durch eine *Allowance* antizipiert — nach dem "
        "*Matching Principle* in der Periode des Umsatzes. Methoden: "
        "*Percentage of Sales*, *Aging Method* oder *Specific Identification*.\n"
        "- **DSO (Days Sales Outstanding):** Wie viele Tage vergehen zwischen "
        "Umsatz und Zahlungseingang? Ein steigender DSO ist ein Warnsignal.\n"
        "- **Factoring:** Der Verkauf von Forderungen — *With Recourse* "
        "(Risiko bleibt beim Verkäufer) oder *Without Recourse* (True Sale, "
        "Risiko geht auf den Factor über).\n\n"
        "## Warum es relevant ist\n"
        "Factoring und *Pledging* (Sicherungsabtretung) sind gängige Instrumente "
        "der Liquiditätssteuerung. Der CFO muss die bilanziellen und "
        "wirtschaftlichen Unterschiede kennen — und erkennen, wenn andere "
        "Unternehmen ihre Zahlen durch aggressive Revenue Recognition schönen."
    ),
    "ch5": (
        "**Vorräte** (*Inventories*) und **Anlagevermögen** (*PP&E*) sind "
        "die größten Vermögensposten vieler Industrie- und Handelsunternehmen. "
        "Ihre Bewertung und Abschreibung hat direkte Auswirkungen auf "
        "Gewinn, Steuerlast und Bilanzkennzahlen.\n\n"
        "## Zentrale Konzepte\n"
        "- **FIFO vs. LIFO vs. Durchschnitt:** In Zeiten steigender Preise "
        "führt *FIFO* zu höherem Gewinn (niedrigerer *COGS*), *LIFO* zu "
        "Steuervorteilen (höherer *COGS*). LIFO ist nach IFRS verboten, "
        "nur nach US-GAAP erlaubt.\n"
        "- **Lower of Cost or Market (Niederstwertprinzip):** Vorräte dürfen "
        "maximal zu Anschaffungskosten angesetzt werden. Liegt der Marktwert "
        "darunter, muss abgewertet werden — Wertaufholung ist später möglich.\n"
        "- **CapEx vs. OpEx:** *Capital Expenditures* werden aktiviert und "
        "über die Nutzungsdauer abgeschrieben. Sie schonen kurzfristig die GuV, "
        "belasten aber den *Free Cash Flow*. *Operating Expenses* belasten "
        "das Periodenergebnis sofort.\n\n"
        "## Warum es relevant ist\n"
        "Der *Impairment Test* nach IAS 36 für *PP&E* ist einer der "
        "ermessensstärksten Bereiche der IFRS-Bilanzierung — die Cashflow-Prognosen "
        "für den *Value in Use* bieten erheblichen Spielraum für "
        "*Earnings Management*."
    ),
}

# ─── Book 3: Corporate Finance OER ──────────────────────────────────────────

CORPORATE_INTROS = {
    "ch1": (
        "**Kapitalbudgetierung** (*Capital Budgeting*) ist der Prozess, mit dem "
        "Unternehmen langfristige Investitionsprojekte bewerten und auswählen. "
        "Sie ist das Kerninstrument des CFO, um zu entscheiden, ob eine neue "
        "Fabrik, ein Software-Projekt oder eine Akquisition Wert schafft — "
        "oder Kapital vernichtet.\n\n"
        "## Zentrale Konzepte\n"
        "- **NPV (Net Present Value / Kapitalwert):** Diskontiert alle künftigen "
        "Cashflows mit den Kapitalkosten und zeigt die absolute Wertsteigerung. "
        "NPV > 0 = Wertschaffung. NPV ist theoretisch die einzig korrekte "
        "Entscheidungsregel.\n"
        "- **IRR (Internal Rate of Return):** Der Zinssatz, bei dem *NPV = 0*. "
        "Intuitiv (Prozentzahl), aber mit Schwächen: Multiple *IRRs* bei "
        "wechselnden Cashflow-Vorzeichen und unrealistische Reinvestitionsannahme.\n"
        "- **Payback Period:** Zeit bis zur Amortisation — einfach, aber "
        "ignoriert Zeitwert und Cashflows nach dem Break-Even.\n"
        "- **Real Options (Realoptionen):** Flexibilität im Investitionsprozess — "
        "die Option, ein Projekt zu verschieben, zu erweitern, abzubrechen "
        "oder den Produktmix zu wechseln. Klassischer *NPV* unterschätzt "
        "flexible Projekte.\n\n"
        "## Warum es relevant ist\n"
        "Fehler in der Kapitalbudgetierung sind die teuersten Fehler eines "
        "CFO. Falsche Diskontsätze, optimistische Cashflow-Prognosen oder "
        "ignorierte *Real Options* führen zu Kapitalvernichtung im großen Stil."
    ),
    "ch2": (
        "**Kapitalkosten** und **Kapitalstruktur** bestimmen, wie teuer die "
        "Finanzierung eines Unternehmens ist — und wie sie optimal zwischen "
        "Eigen- und Fremdkapital aufgeteilt wird. Dieses Kapitel verbindet "
        "die Berechnung des *WACC* mit den großen Theorien der Kapitalstruktur.\n\n"
        "## Zentrale Konzepte\n"
        "- **WACC (Weighted Average Cost of Capital):** Die gewichteten "
        "Kapitalkosten aus Eigen- und Fremdkapital, Steuervorteil inklusive. "
        "*WACC* ist der Mindest-Diskontsatz für alle Investitionen gleichen Risikos.\n"
        "- **CAPM (Capital Asset Pricing Model):** *r_E = r_f + β × (r_m − r_f)*. "
        "Das *Beta* misst das systematische Risiko einer Aktie relativ zum Markt. "
        "Beta > 1: zyklisch. Beta < 1: defensiv.\n"
        "- **Modigliani-Miller-Theorem:** Ohne Steuern ist die Kapitalstruktur "
        "irrelevant — der Unternehmenswert hängt nur von den Cashflows ab. "
        "Mit Steuern wird Fremdkapital wertvoll (Zinsabzug = *Tax Shield*). "
        "Die Realität: *Trade-Off Theory* zwischen *Tax Shield* und "
        "Insolvenzkosten.\n"
        "- **Pecking Order Theory:** Unternehmen bevorzugen zuerst Innenfinanzierung, "
        "dann Fremdkapital, zuletzt Eigenkapital — weil jede externe "
        "Finanzierung *Informationsasymmetrie* signalisiert.\n\n"
        "## Warum es relevant ist\n"
        "Die Wahl der Kapitalstruktur ist eine der strategischsten "
        "Entscheidungen eines CFO. Branchen mit stabilen Cashflows (Versorger) "
        "können mehr *Debt* tragen als zyklische Branchen (Automobilbau)."
    ),
    "ch3": (
        "**Unternehmensbewertung** (*Company Valuation*) ist die Kunst, den "
        "wirtschaftlichen Wert eines Unternehmens zu bestimmen — für "
        "Akquisitionen, Börsengänge, faire Kaufpreise oder strategische "
        "Entscheidungen. Dieses Kapitel führt in die drei Standardmethoden "
        "der Bewertungspraxis ein.\n\n"
        "## Zentrale Konzepte\n"
        "- **DCF-Methode (Discounted Cash Flow):** Der Unternehmenswert ist "
        "der Barwert aller künftigen *Free Cash Flows*. Der *Terminal Value* "
        "(Endwert nach der Detailprognose) macht oft 60-80% des Gesamtwerts aus — "
        "enormer Hebel über die ewige Wachstumsrate *g*.\n"
        "- **Comparable Company Analysis (Trading Multiples):** Vergleich mit "
        "börsennotierten *Peers*. Die wichtigsten Multiples sind *EV/EBITDA* "
        "(kapitalstrukturneutral), *P/E*, *EV/Sales* und *P/B*.\n"
        "- **Enterprise Value vs. Equity Value:** *EV* ist der Wert des gesamten "
        "operativen Geschäfts (für alle Kapitalgeber). *Equity Value* = "
        "EV − Net Debt − Minorities − Pension Obligations — der Wert "
        "für die Aktionäre.\n"
        "- **Precedent Transactions:** Historische M&A-Transaktionen mit "
        "*Control Premium* (20-40% Aufschlag auf den Börsenkurs).\n\n"
        "## Warum es relevant ist\n"
        "Bewertung ist nie exakt, aber immer notwendig. Ein CFO muss verstehen, "
        "welche Methodik für welchen Zweck angemessen ist — und wie man "
        "Bewertungsspielräume kritisch hinterfragt."
    ),
    "ch4": (
        "**Working Capital Management** ist das Management der kurzfristigen "
        "Zahlungsfähigkeit eines Unternehmens. Es geht um die Optimierung "
        "des Dreiklangs aus Forderungen (*DSO*), Verbindlichkeiten (*DPO*) "
        "und Vorräten (*DIO*) — und die Frage, wie viel Liquidität "
        "im Tagesgeschäft gebunden ist.\n\n"
        "## Zentrale Konzepte\n"
        "- **Cash Conversion Cycle (CCC):** *DIO + DSO − DPO*. Das Ziel: "
        "den *CCC* minimieren. Ein negativer *CCC* (wie bei Amazon) bedeutet, "
        "dass Kunden zahlen, bevor Lieferanten bezahlt werden müssen — "
        "kostenlose Finanzierung durch die Lieferantenkette.\n"
        "- **Credit Policy:** Der Trade-Off zwischen großzügigen Zahlungszielen "
        "(mehr Umsatz, mehr Kreditrisiko) und strikter *Credit Policy* "
        "(weniger Ausfälle, weniger Umsatz). Die Entscheidung folgt einer "
        "*NPV*-Logik.\n"
        "- **Inventory Management:** *EOQ (Economic Order Quantity)* für "
        "optimale Bestellmengen, *Just-in-Time* für minimale Lagerbestände.\n"
        "- **Trade Credit (Lieferantenkredit):** *2/10 net 30* bedeutet "
        "2% Skonto bei Zahlung in 10 Tagen. Skontoverzicht entspricht "
        "einem effektiven Jahreszins von ~37% — extrem teuer.\n\n"
        "## Warum es relevant ist\n"
        "*Working Capital* ist der größte Hebel für kurzfristige "
        "Liquiditätssteuerung — und eine der häufigsten Stellschrauben "
        "für Cash-Effekte im Unternehmen. Der CFO muss die optimale "
        "Balance aus Liquidität, Rentabilität und Risiko finden."
    ),
}

# ─── Apply to all three books ──────────────────────────────────────────────

def add_intros_to_chapters(data, intros):
    for ch in data["chapters"]:
        cid = ch["id"]
        if cid in intros:
            ch["intro"] = intros[cid]
        else:
            print(f"  ⚠ No intro for {cid}")
    return data

base = "/data/.openclaw/workspace/projects/learning-hub/content/cfo-finance"

files = [
    f"{base}/principles-of-finance.json",
    f"{base}/mit-financial-accounting.json",
    f"{base}/corporate-finance-oer.json",
]
introsets = [PRINCIPLES_INTROS, MIT_INTROS, CORPORATE_INTROS]

for fpath, iset in zip(files, introsets):
    print(f"\n📘 {fpath.split('/')[-1]}")
    data = load_json(fpath)
    data = add_intros_to_chapters(data, iset)
    save_json(fpath, data)

print("\n✅ Done — all chapter intros added.")
