<h1 align="center">
  🤖 MCPServe by @ryaneggz
</h1>

<p align="center">
Simple MCP Server w/ Shell Exec. Connect to Local via Ngrok, or Host Ubuntu24 Container in Docke
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/View%20Documentation-Docs-yellow"></a>
  <a href="https://join.slack.com/t/promptengineersai/shared_invite/zt-21upjsftv-gX~gNjTCU~2HfbeM_ZwTEQ"><img src="https://img.shields.io/badge/Join%20our%20community-Slack-blue"></a>
</p>

<p align="center">
  <img src="#" width="600px" />
</p>

## 📖 Table of Contents

- [Deploy](https://github.com/promptengineers-ai/llm-server/blob/development/docs/deploy)

## 🛠️ Setup Local Hosted MCP

```bash
## Install uv (if you not using you late to party)
curl -LsSf https://astral.sh/uv/install.sh | sh

## Create virtual environment
uv venv
source .venv/bin/activate

## Install Dependencies
uv pip install -r requirements.txt

## Start localhost MCPServe
python main.py
```

## 🛠️ Setup Docker Hosted MCP

```bash
docker compose up --build
```

## Client MCP Config

If you have configured auth server side in your code you can enable headers for API.
Have found this requires some code changes to the mcp librarie Settings. Adding a middleware prop. :/

```json
{
  "terminal": {
    "transport": "sse",
    "url": "http://localhost:8005/sse",
    // "headers": {
    //     "x-api-key": "abcdef123456..."
    // }
  }
}
```

## 🚀 Roadmap

- [ ] 🤖 Coming Soon...

Create an issue and lets start a discussion if you'd like to see a feature added to the roadmap.

## 💡 Issues

Feel free to submit issues and enhancement requests. We're always looking for feedback and suggestions.

## 🤓 Maintainers

- `Ryan Eggleston` - `@ryaneggz`

## 📜 License

This project is open-source, under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you please.
