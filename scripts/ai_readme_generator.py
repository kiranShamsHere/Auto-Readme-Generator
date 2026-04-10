#!/usr/bin/env python3
"""
AI-Powered GitHub README Generator using Groq (Free)
"""

import os
import json
import time
from pathlib import Path
from github import Github, GithubException
from groq import Groq
import logging
from datetime import datetime

# ─── Logging ─────────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
SKIP_REPOS = {
    "Auto-Readme-Generator",
    "kiranShamsHere",
    "Github-Username-Updater",
}

# ─── Repo Analyzer ───────────────────────────────────────────────────────────
class RepoAnalyzer:
    def __init__(self, repo):
        self.repo = repo

    def file_tree(self, limit=35):
        try:
            items = self.repo.get_contents("")
            icons = {
                '.py':'🐍', '.js':'📜', '.ts':'📘', '.jsx':'⚛️', '.tsx':'⚛️',
                '.html':'🌐', '.css':'🎨', '.json':'📋', '.md':'📝',
                '.php':'🐘', '.go':'🐹', '.sh':'🔨', '.yml':'⚙️', '.sql':'💾',
            }
            lines = []
            for item in items[:limit]:
                if item.type == "dir":
                    lines.append(f"📁 {item.name}/")
                else:
                    ext = Path(item.name).suffix
                    lines.append(f"{icons.get(ext, '📄')} {item.name}")
            return "\n".join(lines)
        except:
            return "(could not read files)"

    def detect_stack(self):
        techs = []
        try:
            pkg = self.repo.get_contents("package.json")
            data = json.loads(pkg.decoded_content)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "react" in deps or "react-dom" in deps: techs.append("React")
            if "next" in deps: techs.append("Next.js")
            if "vue" in deps: techs.append("Vue.js")
            if "express" in deps: techs.append("Express.js")
            if "typescript" in deps: techs.append("TypeScript")
            if "tailwindcss" in deps: techs.append("Tailwind CSS")
            if "vite" in deps: techs.append("Vite")
            techs.append("JavaScript")
        except: pass

        try:
            req = self.repo.get_contents("requirements.txt")
            reqs = req.decoded_content.decode().lower()
            if "django" in reqs: techs.append("Django")
            if "flask" in reqs: techs.append("Flask")
            if "fastapi" in reqs: techs.append("FastAPI")
            techs.append("Python")
        except: pass

        try:
            names = [i.name for i in self.repo.get_contents("")]
            if any(n.endswith(".html") for n in names) and "HTML" not in techs:
                techs.append("HTML")
            if any(n.endswith(".css") for n in names) and "CSS" not in techs:
                techs.append("CSS")
            if any(n.endswith(".php") for n in names): techs.append("PHP")
        except: pass

        return list(dict.fromkeys(techs)) or [self.repo.language or "Web"]

    def analyze(self):
        return {
            "name": self.repo.name,
            "description": self.repo.description or "",
            "url": self.repo.html_url,
            "language": self.repo.language or "Unknown",
            "topics": self.repo.topics or [],
            "tree": self.file_tree(),
            "stack": self.detect_stack(),
        }


# ─── Groq README Generator ───────────────────────────────────────────────────
class GroqReadmeGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate(self, a: dict) -> str:
        stack = ", ".join(a["stack"]) if a["stack"] else a["language"]
        topics = ", ".join(a["topics"]) if a["topics"] else "none"

        prompt = f"""Create a professional, well-formatted GitHub README.md for this repository.

REPO DETAILS:
- Name: {a['name']}
- Description: {a['description'] or 'A project by kiranShamsHere'}
- Language: {a['language']}
- Stack: {stack}
- Topics: {topics}
- URL: {a['url']}

FILE STRUCTURE:
{a['tree']}

INSTRUCTIONS:
- Write unique content specific to this project — not generic filler
- Use emojis for section headers
- Include these sections: title + badges, description, features, tech stack, project structure, installation, usage, author, license
- Add shields.io badges at top for language and license
- Author: kiranShamsHere — Full Stack Developer & AgriClima AI Consultant — GitHub @kiranShamsHere
- Output ONLY valid Markdown. No explanations, no preamble."""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.7,
        )
        return response.choices[0].message.content


# ─── GitHub Manager ───────────────────────────────────────────────────────────
class GitHubManager:
    def __init__(self, token: str):
        self.gh = Github(token)
        self.user = self.gh.get_user()

    def has_readme(self, repo) -> bool:
        try:
            repo.get_contents("README.md")
            return True
        except GithubException:
            return False

    def upsert_readme(self, repo, content: str) -> bool:
        try:
            if self.has_readme(repo):
                existing = repo.get_contents("README.md")
                repo.update_file(
                    "README.md",
                    "docs: ✨ Redesign README with AI",
                    content,
                    existing.sha,
                )
                log.info(f"  ✅ Updated  → {repo.name}")
            else:
                repo.create_file(
                    "README.md",
                    "docs: ✨ Generate AI README",
                    content,
                    branch=repo.default_branch,
                )
                log.info(f"  ✅ Created  → {repo.name}")
            return True
        except Exception as e:
            log.error(f"  ❌ Failed   → {repo.name}: {e}")
            return False

    def run(self, force: bool, ai: GroqReadmeGenerator):
        log.info("=" * 60)
        log.info("🚀 Starting README Generator (Groq - Free)")
        log.info(f"   Force regenerate: {force}")
        log.info("=" * 60)

        repos = list(self.user.get_repos(sort="updated", direction="desc"))
        stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0}

        for repo in repos:
            stats["total"] += 1
            name = repo.name

            if name in SKIP_REPOS:
                log.info(f"  ⏭️  Skip (protected)  → {name}")
                stats["skipped"] += 1
                continue

            if repo.archived:
                log.info(f"  ⏭️  Skip (archived)   → {name}")
                stats["skipped"] += 1
                continue

            if not force and self.has_readme(repo):
                log.info(f"  ⏭️  Skip (has readme) → {name}")
                stats["skipped"] += 1
                continue

            log.info(f"  🔍 Processing → {name}")
            try:
                analysis = RepoAnalyzer(repo).analyze()
                readme = ai.generate(analysis)
                if self.upsert_readme(repo, readme):
                    stats["updated"] += 1
                else:
                    stats["errors"] += 1
                time.sleep(1.5)  # stay within Groq rate limits
            except Exception as e:
                log.error(f"  ❌ Error → {name}: {e}")
                stats["errors"] += 1
                time.sleep(3)   # back off on error

        log.info("=" * 60)
        log.info("📊 Summary")
        log.info(f"   Total scanned  : {stats['total']}")
        log.info(f"   Created/Updated: {stats['updated']} ✅")
        log.info(f"   Skipped        : {stats['skipped']}")
        log.info(f"   Errors         : {stats['errors']} ❌")
        log.info("=" * 60)


# ─── Entry Point ─────────────────────────────────────────────────────────────
def main():
    gh_token = os.environ.get("GH_TOKEN")
    groq_key = os.environ.get("GROQ_API_KEY")
    force = os.environ.get("FORCE_REGENERATE", "true").lower() == "true"

    if not gh_token:
        log.error("❌ GH_TOKEN not set"); return
    if not groq_key:
        log.error("❌ GROQ_API_KEY not set"); return

    ai = GroqReadmeGenerator(groq_key)
    GitHubManager(gh_token).run(force=force, ai=ai)


if __name__ == "__main__":
    main()