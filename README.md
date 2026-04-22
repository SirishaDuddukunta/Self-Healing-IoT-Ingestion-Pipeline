#  Sentinel: Self-Healing AI Ingestion Pipeline

**Sentinel** is a high-performance, asynchronous guardrail service designed for high-frequency IoT platforms. It sits between raw telemetry streams and downstream ML models to ensure that data "drift" or "noise" never breaks your production environment.



###  Key Features
* **Asynchronous Ingestion:** Built on **FastAPI** to handle concurrent high-volume streaming data.
* **Modular Plugin Architecture:** Uses an Abstract Base Class (ABC) pattern, allowing new validation or AI rules to be added without changing the core engine.
* **AI-Powered Guardrails:**
    * **Anomaly Detection:** Statistical Z-Score analysis to identify outliers based on historical norms.
    * **Self-Healing (Imputation):** Automatic data recovery using historical mean regression when noise is detected.
* **Confidence Scoring:** Every batch returns a confidence grade. Scores below **0.7** are automatically routed to a background **Review Queue**.



### 📂 Repository Structure
```text
.
├── main.py              # FastAPI application & Orchestration logic
├── models.py            # Pydantic data schemas (Strict validation)
├── plugins.py           # ABC Interface and AI Plugin implementations
├── Dockerfile           # Containerization instructions
├── docker-compose.yml   # Orchestration for easy deployment
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```


### 🛠️ Setup & Installation

#### Option 1: Using Docker (Recommended)
This is the fastest way to get the service running in a production-like environment.
1.  **Build and Start:**
    ```bash
    docker-compose up --build
    ```
2.  **Access UI:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

#### Option 2: Local Manual Setup
1.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Server:**
    ```bash
    python main.py
    ```


###  Testing the Pipeline
Once the Swagger UI is running at `/docs`:

1.  **Test Case 1: Healthy Data**
    * **Input:** Send a value close to `20.0` (e.g., `21.5`).
    * **Result:** `status: accepted`, `confidence_score: 1.0`.
2.  **Test Case 2: Anomaly & Self-Healing**
    * **Input:** Send an outlier (e.g., `500.0`).
    * **Result:** `status: flagged_for_review`, `confidence_score: 0.4`.
    * **Healing:** The `data.value` in the response is automatically corrected to `20.12`.

###  Design Decisions
* **FastAPI & Async:** IoT ingestion requires non-blocking I/O. Using `async/await` ensures the service remains responsive during heavy bursts of sensor data.
* **Plugin Pattern:** Follows the **Open/Closed Principle**. You can add new logic (e.g., *Isolation Forest* or *Range Checks*) by adding a new class to `plugins.py` without modifying the core API logic.
* **Background Tasks:** Routing low-confidence data to the **Review Queue** is handled as a background task to ensure zero latency impact on the primary ingestion response.
* **Code Hygiene:** Implements PEP 8 standards, strict type hinting, and modular file separation for enterprise-grade maintainability.
