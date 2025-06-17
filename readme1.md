# 🤖 Multi-AI Agent System using Python + Semantic Kernel

A **production-grade multi-agent orchestration system** built with [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) in Python. This app demonstrates how autonomous agents can collaboratively plan, write, review, and submit code securely and reliably.

---

## 🚀 Features

✅ **Multi-Agent AI Collaboration**

✅ **Secure Code Execution with Docker Sandbox**

✅ **Automatic GitHub Pull Request Creation**

✅ **Context-Aware Memory with Vector Store**

✅ **Task Completion Email Notification**

✅ **Semantic Kernel GroupChat & Orchestration**

✅ **Industry-Ready Observability & Logging**

✅ **Pluggable, Extensible Architecture**

---

## 🧠 What is this?

This system simulates a real-world **software development pipeline** driven by multiple AI agents. Each agent has a dedicated responsibility, and they **collaborate in a controlled orchestration loop**.

The agents include:

| Agent       | Role                                                                 |
|-------------|----------------------------------------------------------------------|
| `Planner`   | Breaks down the user task into actionable steps                     |
| `Writer`    | Writes Python code based on the plan                                |
| `Sanitizer` | Validates and executes code in a secure Docker sandbox              |
| `Reviewer`  | Reviews and approves the generated code                             |
| `GitAgent`  | Creates a branch, commits the code, and opens a GitHub PR           |
| `Notifier`  | Sends an email to the user with the pull request or completion info |

Agents communicate through **Semantic Kernel's GroupChat**, governed by the `ApprovalTerminationStrategy` to ensure high-quality results before completing the task.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[User Input Task] --> B[Planner Agent]
    B --> C[Writer Agent]
    C --> D[Sanitizer (Docker Sandbox)]
    D --> E[Reviewer Agent]
    E -->|If Approved| F[GitAgent -> GitHub PR]
    F --> G[Notifier -> Email]
```

**Orchestration:** Semantic Kernel’s `GroupChatOrchestration` manages agent interactions, looping until the task is completed or rejected.

---

## 🔧 Tech Stack

- **Language:** Python 🐍
- **AI Orchestration:** Semantic Kernel 🤖
- **LLM Backend:** OpenAI GPT-4 via `OpenAIChatCompletion`
- **Security:** Docker-based sandboxing
- **Memory:** In-Memory Vector Store (can be swapped with Pinecone, Redis, etc.)
- **Notifications:** SMTP via `aiosmtplib`
- **Git Integration:** GitHub API via `PyGithub`

---

## 📁 Project Structure

```
multiai_agent_system.py      # All logic: agents, plugins, orchestrator
.env                         # Environment variables (OPENAI keys, SMTP creds)
README.md                    # You're reading this
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/multiai-agent-system.git
cd multiai-agent-system
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install semantic-kernel openai docker pygithub aiosmtplib
```

### 4. Create a `.env` file

Create a file named `.env` and add the following:

```env
OPENAI_API_KEY=your-openai-api-key
SMTP_HOST=smtp.yourprovider.com
SMTP_USER=youremail@example.com
SMTP_PASS=yourpassword
GITHUB_TOKEN=your-github-token
```

Ensure you also have Docker running locally.

---

## ▶️ Run the System

```bash
python multiai_agent_system.py
```

---

## ✉️ How the Notification Works

The `Notifier` agent uses SMTP to send you an email when:

- The PR is created (with its link)
- Or when task execution completes

---

## 🔐 Security Practices

- **Docker sandbox** is used for untrusted code execution with:
  - Memory limits
  - No networking
  - `no-new-privileges`
- GitHub tokens are securely used via environment variables
- Email sending uses authenticated and TLS-secured SMTP

---

## 🔄 Orchestration Loop

This system uses `GroupChatOrchestration` with:

- **ConcurrentOrchestration** if extended to handle parallel files
- **ApprovalTerminationStrategy** to wait for explicit `Reviewer` approval

---

## 💡 Future Enhancements

- ✅ Real-time dashboard using FastAPI or Flask
- ✅ Replace memory with Redis/Pinecone for persistence
- ✅ Slack/Discord webhook notifications
- ✅ Add CI/CD workflows for automatic testing of AI-generated code
- ✅ Integrate with LangGraph for stateful workflows

---

## 🧠 Why Semantic Kernel?

Semantic Kernel gives us a **programmable orchestrator layer** over LLMs, enabling:
- AI agent memory
- Plugins with native Python code
- Group conversations between agents
- Strategy-based task termination
- Tight LLM + API integration

---

## 📬 Need Help?

Feel free to raise an issue or contact the maintainers.

---

## 📜 License

[MIT License](LICENSE)

---

## 🙌 Credits

- [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [OpenAI](https://openai.com/)
- [PyGithub](https://pygithub.readthedocs.io/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)
