import os
import logging
import asyncio
import openai
import docker
import tempfile
import smtplib
from email.mime.text import MIMEText
from github import Github
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.planning import FunctionCallingStepwisePlanner
from semantic_kernel.memory.memory_store import VolatileMemoryStore
from semantic_kernel.orchestration.groupchat import GroupChat, GroupChatParticipant
from semantic_kernel.orchestration.groupchat import GroupChatOrchestrator
from semantic_kernel.orchestration.groupchat.group_chat_config import GroupChatConfig
from semantic_kernel.orchestration.groupchat.group_chat_completion_client import GroupChatCompletionClient
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin

# -------- Setup Logging -------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------- Load Secrets -------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "yourusername/yourrepo"

# -------- Semantic Kernel Init -------- #
kernel = Kernel()
kernel.add_text_completion_service("openai-gpt", OpenAIChatCompletion("gpt-4", OPENAI_API_KEY))
kernel.import_plugin_from_object(TextMemoryPlugin(), plugin_name="text_memory")
kernel.register_memory_store(VolatileMemoryStore())

# -------- Helper: Send Email -------- #
def send_email(subject, body, recipient):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = recipient

        with smtplib.SMTP_SSL(SMTP_HOST, 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info("📬 Email sent successfully")
    except Exception as e:
        logger.error(f"Email send failed: {e}")

# -------- Helper: Docker Sandbox Executor -------- #
def execute_code_in_docker(code: str) -> str:
    client = docker.from_env()
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            code_file = os.path.join(tempdir, "script.py")
            with open(code_file, "w") as f:
                f.write(code)

            container = client.containers.run(
                image="python:3.10",
                command="python script.py",
                volumes={tempdir: {"bind": "/code", "mode": "ro"}},
                working_dir="/code",
                detach=True,
                network_disabled=True,
                mem_limit="128m",
                security_opt=["no-new-privileges"]
            )

            result = container.logs(stdout=True, stderr=True)
            container.remove(force=True)
            return result.decode()
    except Exception as e:
        logger.error(f"Docker execution failed: {e}")
        return f"Execution failed: {str(e)}"

# -------- Helper: GitHub Commit & PR -------- #
def create_github_pr(file_path: str, content: str, commit_msg: str):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        branch = repo.get_branch("main")
        new_branch_name = "auto/feature-agent"
        repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=branch.commit.sha)
        repo.create_file(path=file_path, message=commit_msg, content=content, branch=new_branch_name)
        pr = repo.create_pull(
            title="🤖 AI Agent: New Code Contribution",
            body="This PR was created by the multi-agent AI system.",
            head=new_branch_name,
            base="main"
        )
        logger.info(f"✅ Pull request created: {pr.html_url}")
        return pr.html_url
    except Exception as e:
        logger.error(f"GitHub PR failed: {e}")
        return None

# -------- Define the Agents -------- #
planner_prompt = """
You're the Planner. Based on the user's request, break down the task into steps. 
Respond in a concise, numbered list of actions.
"""

writer_prompt = """
You're the Writer. Based on the plan, write correct and clean Python code. Do not include any explanation.
"""

sanitizer_prompt = """
You're the Sanitizer. Check the Python code for syntax errors or dangerous operations.
If safe, say 'SAFE'. If not, explain the issue.
"""

reviewer_prompt = """
You're the Reviewer. Review the generated code for quality and correctness.
If it's okay, say 'APPROVED'. Otherwise, list improvements.
"""

notifier_prompt = """
You're the Notifier. Format a short summary message to email the user about task completion and provide the PR link.
"""

# -------- Group Chat Setup -------- #
group_chat = GroupChat(
    system_description="AI team collaborating to complete coding tasks.",
    initial_message="Let's begin the task.",
    participants=[
        GroupChatParticipant(name="Planner", role="Planner", prompt=planner_prompt),
        GroupChatParticipant(name="Writer", role="Writer", prompt=writer_prompt),
        GroupChatParticipant(name="Sanitizer", role="Sanitizer", prompt=sanitizer_prompt),
        GroupChatParticipant(name="Reviewer", role="Reviewer", prompt=reviewer_prompt),
        GroupChatParticipant(name="Notifier", role="Notifier", prompt=notifier_prompt),
    ]
)

# -------- Orchestrator -------- #
orchestrator = GroupChatOrchestrator(GroupChatCompletionClient(kernel), group_chat)

# -------- Main Execution -------- #
async def run_agents(user_task: str, user_email: str):
    logger.info(f"🎯 Task: {user_task}")
    chat_history = f"User wants: {user_task}"
    message = await orchestrator.step(chat_history)

    # Extract and generate code
    for _ in range(5):
        message = await orchestrator.step(message)

    # Final decision logic
    code = message.content if "def " in message.content else None
    if not code:
        logger.warning("⚠️ No code generated.")
        return

    logger.info("🧪 Running Docker sandbox...")
    output = execute_code_in_docker(code)
    logger.info(f"🚀 Output:\n{output}")

    if "SAFE" not in output:
        logger.warning("❌ Code failed sandbox check.")
        return

    pr_link = create_github_pr("generated_code.py", code, "Add AI-generated feature")
    if pr_link:
        email_body = f"🎉 Task complete! PR: {pr_link}"
        send_email("✅ Your AI Task is Done", email_body, user_email)
    else:
        logger.warning("⚠️ PR creation failed.")

# -------- Trigger -------- #
if __name__ == "__main__":
    task = input("📝 Enter your task (e.g., 'Write a memoized factorial function'): ")
    email = input("📧 Enter your email address to receive notification: ")

    asyncio.run(run_agents(task, email))
