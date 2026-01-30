# RAI Bootcamp Demo: Groundedness & Harmful Content Evaluation

A lightweight demonstration project showcasing how to evaluate Responsible AI (RAI) risks using **Azure AI Foundry Safety Evaluations SDK**. This project demonstrates:

- 🔍 **Retrieval-Augmented Generation (RAG)** chat that answers questions from configurable SharePoint sources
- 🛡️ **Automated RAI Risk Evaluation** for groundedness and harmful content
- 🔐 **Entra ID Authentication Only** (no hardcoded keys)
- 🏗️ **Resource Separation**: inference in East US, evaluation in East US 2 (where Safety Evaluations SDK is supported)

---

## Quick Start

### 1. Prerequisites

- Python 3.8 or later
- Azure subscription with access to:
  - **Main Azure OpenAI deployment** in East US with a chat deployment (e.g., `gpt-4o-mini`)
  - **Azure AI Foundry resource** in East US 2 or other supported region for Safety Evaluations SDK
  - Entra ID credentials (via Azure CLI: `az login`)

### 2. Setup

```bash
# Clone or navigate to the project
cd rai-rai-bootcamp-demo

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp env.sample .env

# Edit .env with your resource details
# Required:
#   AZURE_OPENAI_ENDPOINT
#   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
#   EVAL_OPENAI_ENDPOINT
#   EVAL_AZURE_AI_PROJECT_NAME
#   EVAL_AZURE_RESOURCE_GROUP
#   EVAL_AZURE_SUBSCRIPTION_ID
```

### 3. Run the Demo

#### Step 1: Prepare Data (Fetch & Cache SharePoint)
```bash
python scripts/prep_data.py
```
This fetches the three configured webpages, cleans HTML, chunks text, and caches locally.

#### Step 2: Chat with Retrieval
```bash
python scripts/run_chat.py
```
Interactive CLI: ask questions, get answers grounded in cached webpage content with citations.

Example questions:
- "What is Responsible AI?"
- "What does accountability principle mean in RAI?"

#### Step 3: Run Safety Evaluations
```bash
python scripts/run_eval.py
```
Runs predefined evaluation scenarios:
- **Groundedness**: checks if answers are grounded in source context
- **Harmful Content**: detects hate, sexual, violent, or self-harm content

Results saved to:
- `evaluation/reports/groundedness_results.json`
- `evaluation/reports/harmful_content_results.json`

---

## Architecture

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Config Loader** | Load env, sources, scenarios | `app/config_loader.py` |
| **Auth** | Entra ID token acquisition | `app/auth.py` |
| **Retrieval** | Fetch SharePoint → chunk → score | `app/retrieval.py` |
| **LLM** | Inference endpoint wrapper | `app/llm.py` |
| **Chat App** | Compose retrieval + LLM | `app/chat.py` |
| **Evaluators** | QAEvaluator + ContentSafetyEvaluator | `evaluation/evaluators_wrapper.py` |
| **Evaluation Runner** | Orchestrate evals | `evaluation/runner.py` |

### Resource Separation

**Inference** (East US):
- Uses `AZURE_OPENAI_ENDPOINT` for chat LLM
- For application Q&A answering

**Evaluation** (East US 2 or supported region):
- Uses `EVAL_OPENAI_ENDPOINT` for Safety Evaluations SDK
- For groundedness & harmful content assessment
- Completely separate token and credential scope

---

## Configuration

### Environment Variables (`.env`)

**Inference Resource**
```
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Evaluation Resource**
```
EVAL_OPENAI_ENDPOINT=https://<your-eval-resource-name>.openai.azure.com/
EVAL_AZURE_AI_PROJECT_NAME=<your-ai-foundry-project-name>
EVAL_AZURE_RESOURCE_GROUP=<your-resource-group>
EVAL_AZURE_SUBSCRIPTION_ID=<your-subscription-id>
```

### Webpage Sources

Edit `config/sources.json` to customize web sources (no code changes needed):
```json
[
  {
    "name": "...",
    "url": "https://microsoft.sharepoint.com/...",
    "description": "..."
  }
]
```

### Evaluation Scenarios

Edit `evaluation/scenarios/default_scenarios.jsonl` to add/modify test cases:
```json
{
  "query": "How do I troubleshoot auth errors?",
  "response": "Based on Identity Support page...",
  "context": "The Identity-SRE-Support page provides...",
  "ground_truth": "Full source text",
  "category": "groundedness"
}
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov=evaluation --cov-report=html
```

---

## 15–20 Minute Live Demo

1. **Setup** (1 min): Show env separation (inference vs. evaluation resources)
2. **Sources** (1 min): Show `config/sources.json` (configurable, no code changes)
3. **Data Prep** (2 min): Run `prep_data.py`; show chunks cached
4. **Chat** (4 min): Run `run_chat.py`; ask 2–3 questions; show answers + citations
5. **Scenarios** (1 min): Display sample rows from `default_scenarios.jsonl`
6. **Evaluation** (6 min): Run `run_eval.py`; show groundedness + harmful content scores in reports
7. **Wrap-Up** (2 min): Recap separation, simplicity, readiness for DSB review

---

## Key Concepts

### Groundedness
Measures whether the model's response is grounded in the provided source context (e.g., SharePoint pages). The `QAEvaluator` compares the response against context chunks to ensure answers aren't fabricated.

### Harmful Content
Detects harmful text categories: Hate & Unfairness, Sexual, Violence, Self-Harm. The `ContentSafetyEvaluator` flags responses that may violate safety policies.

### Entra ID Authentication
Uses `DefaultAzureCredential` from Azure Identity SDK. Credential chain:
1. Azure CLI (`az login`)
2. Managed Identity (if running in Azure)
3. Interactive browser login (fallback)

No API keys stored in code or `.env`.

---

## Project Structure

```
rai-rai-bootcamp-demo/
├── README.md
├── env.sample
├── requirements.txt
├── .gitignore
├── config/
│   ├── sources.json             # Configurable SharePoint URLs
│   └── (eval scenarios added in Step 7)
├── app/
│   ├── __init__.py
│   ├── auth.py                  # Entra ID token acquisition
│   ├── config_loader.py         # Load env + config files
│   ├── llm.py                   # Inference LLM wrapper
│   ├── retrieval.py             # SharePoint fetch + chunk + score
│   └── chat.py                  # RAG chat pipeline
├── evaluation/
│   ├── __init__.py
│   ├── evaluators_config.py     # Eval resource config
│   ├── evaluators_wrapper.py    # QAEvaluator + ContentSafetyEvaluator
│   ├── runner.py                # Evaluation orchestrator
│   ├── scenarios/
│   │   └── default_scenarios.jsonl  # Test cases (added in Step 7)
│   └── reports/
│       └── (JSON/CSV results)
├── scripts/
│   ├── prep_data.py             # Fetch + cache web content
│   ├── run_chat.py              # CLI chat entrypoint
│   └── run_eval.py              # Evaluation entrypoint
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_auth.py
    ├── test_retrieval.py
    ├── test_llm.py
    └── test_eval_data_format.py
```

---

## Troubleshooting

**401 Unauthorized (Entra ID)**
- Ensure you've run `az login`
- Check resource endpoint URLs in `.env`

**429 Rate Limit (Inference)**
- Increase TPM (Tokens Per Minute) on the deployment in Azure Portal

**Region Not Supported (Evaluation)**
- Verify `EVAL_OPENAI_ENDPOINT` is in a supported region (East US 2, Sweden Central, France Central, etc.)
- Check [Azure AI Safety Evaluations region support](https://docs.microsoft.com/en-us/azure/ai-studio/how-to/evaluate-sdk)

**SharePoint Access Denied**
- Ensure Entra ID account has access to SharePoint sites
- Check network/firewall (may need to run from corporate network or VPN)

---

## Next Steps

- Extend evaluation with additional scenarios
- Integrate with CI/CD for continuous safety monitoring
- Export results to Excel and upload to OneRAI for formal DSB review
- Customize retrieval scoring (currently simple TF-IDF; can add semantic search)

---

## References

- [Azure AI Foundry Safety Evaluations](https://docs.aml-babel.com/tools/azure-ai-evaluation/)
- [Azure AI Evaluation SDK Python Reference](https://aka.ms/azureaieval-python-ref)
- [Responsible AI Requirements](https://eng.ms/docs/initiatives/ai-safety-security/compliance/dsbreview/requirements/evaluaterisks)
- [Azure Identity SDK (Entra ID)](https://docs.microsoft.com/en-us/python/api/azure-identity/)

---

## License

Internal Microsoft project. See LICENSE in parent directory.
