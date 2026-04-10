#!/usr/bin/env python3
"""
AI-Powered GitHub README Generator using Claude
Redesigns ALL repos or only missing ones, skips specified repos
"""

import os
import json
import time
from pathlib import Path
from github import Github, GithubException
import anthropic
import logging
from datetime import datetime

# ─── Logging ────────────────────────────────────────────────────────────────
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

# ─── Config ─────────────────────────────────────────────────────────────────
SKIP_REPOS = {
    "kiranShamsHere",
    "Github-Username-Updater",
}

# ─── Repo Analyzer ──────────────────────────────────────────────────────────
class RepoAnalyzer:
    def __init__(self, repo):
        self.repo = repo

    def file_tree(self, limit=40):
        try:
            items = self.repo.get_contents("")
            icons = {
                '.py':'🐍','.js':'📜','.ts':'📘','.jsx':'⚛️','.tsx':'⚛️',
                '.html':'🌐','.css':'🎨','.json':'📋','.md':'📝','.java':'☕',
                '.php':'🐘','.go':'🐹','.rs':'🦀','.sh':'🔨','.yml':'⚙️',
                '.yaml':'⚙️','.sql':'💾','.cpp':'⚙️','.c':'🔧',
            }
            lines = []
            for item in items[:limit]:
                if item.type == "dir":
                    lines.append(f"📁 {item.name}/")
                else:
                    ext = Path(item.name).suffix
                    lines.append(f"{icons.get(ext,'📄')} {item.name}")
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
            if "typescript" in deps or "@types/node" in deps: techs.append("TypeScript")
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
            if "numpy" in reqs or "pandas" in reqs: techs.append("Data Science")
            techs.append("Python")
        except: pass

        try:
            items = self.repo.get_contents("")
            names = [i.name for i in items]
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
            "stars": self.repo.stargazers_count,
            "tree": self.file_tree(),
            "stack": self.detect_stack(),
        }


# ─── Claude README Generator ────────────────────────────────────────────────
class ClaudeReadmeGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, a: dict) -> str:
        stack = ", ".join(a["stack"])
        topics = ", ".join(a["topics"]) if a["topics"] else "none"
        prompt = f"""You are an expert technical writer. Create a professional, beautifully formatted GitHub README.md for this repo.

REPO INFO:
- Name: {a['name']}
- Description: {a['description'] or 'Not provided'}
- Language: {a['language']}
- Stack: {stack}
- Topics: {topics}
- URL: {a['url']}

FILE STRUCTURE:
{a['tree']}

REQUIREMENTS:
- Make it unique and specific to this project — no generic boilerplate
- Use emojis tastefully for section headers
- Include: project title, short description, features, tech stack, folder structure, installation, usage, author (kiranShamsHere), license
- Use shields.io badges for language and license at the top
- Write clean, valid Markdown only
- Keep it concise but complete (aim for 150–250 lines)
- Author section: GitHub @kiranShamsHere, Full Stack Developer & AgriClima AI Consultant

Output ONLY the README.md content. No preamble, no explanation."""

        msg = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text


# ─── GitHub Manager ──────────────────────────────────────────────────────────
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

    def run(self, force: bool, ai: ClaudeReadmeGenerator):
        log.info("=" * 60)
        log.info("🚀 Starting AI README Generator")
        log.info(f"   Force regenerate: {force}")
        log.info("=" * 60)

        repos = list(self.user.get_repos(sort="updated", direction="desc"))
        stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0}

        for repo in repos:
            stats["total"] += 1
            name = repo.name

            if name in SKIP_REPOS:
                log.info(f"  ⏭️  Skip (protected) → {name}")
                stats["skipped"] += 1
                continue

            if repo.archived:
                log.info(f"  ⏭️  Skip (archived)  → {name}")
                stats["skipped"] += 1
                continue

            if repo.fork and self.has_readme(repo) and not force:
                log.info(f"  ⏭️  Skip (fork+readme) → {name}")
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
                # Rate limit buffer
                time.sleep(2)
            except Exception as e:
                log.error(f"  ❌ Error → {name}: {e}")
                stats["errors"] += 1

        log.info("=" * 60)
        log.info("📊 Summary")
        log.info(f"   Total scanned : {stats['total']}")
        log.info(f"   Created/Updated: {stats['updated']} ✅")
        log.info(f"   Skipped        : {stats['skipped']}")
        log.info(f"   Errors         : {stats['errors']} ❌")
        log.info("=" * 60)


# ─── Entry Point ─────────────────────────────────────────────────────────────
def main():
    gh_token = os.environ.get("GH_TOKEN")
    ai_key = os.environ.get("ANTHROPIC_API_KEY")
    force = os.environ.get("FORCE_REGENERATE", "true").lower() == "true"

    if not gh_token:
        log.error("❌ GH_TOKEN not set"); return
    if not ai_key:
        log.error("❌ ANTHROPIC_API_KEY not set"); return

    ai = ClaudeReadmeGenerator(ai_key)
    GitHubManager(gh_token).run(force=force, ai=ai)


if __name__ == "__main__":
    main()