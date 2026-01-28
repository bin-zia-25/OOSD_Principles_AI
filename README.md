# ⚖️ Principles AI: SRP & OCP Violation Detector

An intelligent code analysis tool that combines **Machine Learning (Random Forest)** and **Generative AI (Gemini)** to detect and refactor SOLID principle violations in Python code.

---

## 🧠 Core Methodology

This system implements a "Judge and Writer" architecture to move beyond simple static analysis:

1.  **The Judge (Random Forest)**: 
    * Uses a `Scikit-Learn` model trained on custom datasets.
    * Evaluates code features extracted via Abstract Syntax Trees (AST).
    * Makes a probabilistic decision: Is this block healthy or a violation?

2.  **The Writer (Google Gemini)**: 
    * Triggered only when a violation is confirmed by the model.
    * Acts as a Senior Architect to refactor messy code into clean, design-pattern-based solutions.

---

## 📊 Analysis Capabilities

### 1. Open-Closed Principle (OCP)
The model detects code that is "closed for extension" by identifying hardcoded decision logic.
* **Features Tracked**: Total branch count (`if/elif/else`) and String-based comparison risks.
* **Refactor Strategy**: Converts `if-elif` chains into the **Strategy Pattern** or **Polymorphic Classes**.

### 2. Single Responsibility Principle (SRP)
The model identifies classes that are "doing too much".
* **Features Tracked**: Method count, total responsibilities, and LCOM (Lack of Cohesion of Methods) scores.
* **Refactor Strategy**: Splits bloated classes into smaller, focused entities.



---
