# 🔁 LLM Wrapper API

**OpenAI-compatible FastAPI server** for routing chat completions to local or remote LLMs using dynamic YAML configurations.

---

## 🚀 Features

- ✅ OpenAI-compatible `/v1/chat/completions` endpoint  
- ✅ Dynamic model configs via `src/configs/*.yaml`  
- ✅ Server-Sent Events (SSE) support for streaming (`stream=true`)  
- ✅ CLI client with rich output and Markdown rendering  
- ✅ Clean, modular, and testable architecture  
- ✅ Structured logs written to `logs/`  
- ✅ `Taskfile.yml` for simplified dev workflows  

---


## 🛠️ Setup

### Setup 

```bash
task setup
```

---

## 🚦 Run the Server

Start the FastAPI server via Taskfile:

```bash
task run:server
```

Test the endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/models
```

---

## 💬 Run the Client CLI

Start an interactive chat:

```bash
task run:client:interactive
```

Or run a single query:

```bash
task run:client  --query "Explain BGP?"
```

---

## ⚙️ Example Model Config (`src/configs/expert.yaml`)

```yaml
api:
  url: "http://<your-model-host>:8000/v1/chat/completions"

model:
  path: "/path/to/your/model.bin"

system_prompt: |
  You are an expert network engineer answering certification questions concisely and accurately.

parameters:
  temperature: 0.6
  top_p: 0.95
  top_k: 40
  stream: true
```

---

## 📁 Project Structure

```
src/
├── main.py              # Entry point
├── server/
│   ├── main.py          # API app and routes
│   ├── api.py           # LLM proxy logic
│   ├── models.py        # Pydantic models
│   ├── config_loader.py # YAML loader
│   └── config.py        # Env config
├── client/
│   └── cli.py           # CLI with rich output
├── configs/
│   └── expert.yaml      # Example config
```

---

## 📂 Logs

Logs are written to:

```
logs/cli.log      # CLI execution logs (non-interactive)
logs/server.log   # FastAPI server logs
```
---
## ⚙️ Configuration & Secrets

- **Precedence**: Configuration values are loaded in the following order:
  1. `.env` file (using python-dotenv)
  2. Environment variables
  3. Model-specific YAML files under `src/llm_wrapper/configs/`
- **Optional Variables**:
  - `OTLP_ENDPOINT` and `PROMETHEUS_PORT` for telemetry setup
  - `HOST`, `PORT`, `DEFAULT_TIMEOUT`, `STREAMING_TIMEOUT` for server runtime (see `src/llm_wrapper/server/config.py`)
- **Secrets Management**: For production deployments, consider using Docker Secrets or a dedicated secret manager (e.g. AWS Secrets Manager, HashiCorp Vault) instead of committing sensitive values to a `.env` file.

---

## 🧪 Testing

Unit and E2E tests are recommended under a future `tests/` directory.

### Go prototype

An early Go implementation lives in `golang/`. Build and test it with:

```bash
cd golang
go test ./... -cover
go build .
```


---

## 🧰 Requirements

- Python 3.11 or higher  
- [`dev-box`](https://jetify-com.vercel.app/docs/devbox/) for creating isolated shells for development
- [`uv`](https://github.com/astral-sh/uv) for fast dependency management  
- [Task](https://taskfile.dev) for developer automation

---

## 📫 License & Contributions

MIT License. Contributions welcome via pull requests or issues.

## Todo:
* Handle Negative/Offensive prompts: Integrate with prompt shield(prompt-parser service), upgrade the expert.yaml prompt
* Conversation history to be persisted & passed
* Expose an API for consumption
* Authorization: OPA policy, required scopes to be invoked
* Reading `OPENAI_API_KEY` from secrets
* Reading env variables (from env list)
* Loggers & Log Level through env

* Cache Integration : Hold
* Prompt versioning : Hold
