# 🤖 Auto-Readme-Generator

![GitHub repo size](https://img.shields.io/github/repo-size/kiranShamsHere/Auto-Readme-Generator)
![License](https://img.shields.io/github/license/kiranShamsHere/Auto-Readme-Generator)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/kiranShamsHere/Auto-Readme-Generator/ai-readme-generator.yml?label=workflow)

A GitHub Actions workflow that automatically generates and redesigns professional README files for all your repositories using **Groq AI (free)**. No manual writing. No copy-pasting. Just run and done.

---

## 💡 Why I Built This

I had 70+ GitHub repositories — most with missing or poorly written READMEs that didn't reflect the actual project. Writing and formatting a README for every single repo manually was not realistic.

So I built this: a one-click workflow that scans all your repos, analyzes the file structure and tech stack, and generates a unique, professional README for each one automatically.

---

## ✨ What It Does

- 🔍 Scans **all your GitHub repositories** automatically
- 🧠 Detects tech stack (React, Python, HTML/CSS, Node.js, etc.) from repo contents
- ✍️ Generates a **unique README** for each repo using Groq AI (Llama 3)
- 🔄 Can **create missing** READMEs or **redesign existing** ones
- 🛡️ Lets you **protect specific repos** from being touched
- ⏰ Runs on a **weekly schedule** or manually on demand
- 🆓 Completely **free** — uses Groq's free API tier

---

## 🛠️ Tech Stack

- **GitHub Actions** — workflow automation
- **Python 3.11** — core scripting
- **PyGithub** — GitHub API integration
- **Groq API** — free AI (Llama 3.3 70B model)

---

## 📸 Preview

> Workflow running in GitHub Actions:

| Feature | Details |
|---|---|
| AI Model | Llama 3.3 70B (via Groq) |
| Avg. time per repo | ~2 seconds |
| Total run time (70 repos) | ~3-5 minutes |
| Cost | $0 forever |
| Trigger | Manual or every Sunday |

---

## 📂 Project Structure

```
Auto-Readme-Generator/
├── .github/
│   └── workflows/
│       └── ai-readme-generator.yml   # GitHub Actions workflow
├── scripts/
│   └── ai_readme_generator.py        # Main Python script
├── logs/                             # Auto-generated run logs
└── README.md
```

---

## 🚀 How to Use It Yourself

### 1. Fork or clone this repo

```bash
git clone https://github.com/kiranShamsHere/Auto-Readme-Generator.git
cd Auto-Readme-Generator
```

### 2. Get a free Groq API key

- Go to [console.groq.com](https://console.groq.com)
- Sign up → API Keys → Create API Key
- Copy the key

### 3. Create a GitHub Personal Access Token (PAT)

- Go to [github.com/settings/tokens](https://github.com/settings/tokens)
- Generate a token with **repo** scope
- Copy the token

### 4. Add secrets to your repo

Go to your repo → **Settings → Secrets and variables → Actions** → add:

| Secret Name | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GH_PAT_TOKEN` | Your GitHub Personal Access Token |

### 5. Protect repos you don't want touched

In `scripts/ai_readme_generator.py`, edit the `SKIP_REPOS` set:

```python
SKIP_REPOS = {
    "Auto-Readme-Generator",
    "your-profile-repo",
    "any-other-repo-to-skip",
}
```

### 6. Run the workflow

Go to **Actions → 🤖 AI-Powered README Generator → Run workflow**

Set `force_regenerate`:
- `true` → redesign ALL READMEs (existing + missing)
- `false` → only create READMEs for repos that have none

---

## ⚙️ Automatic Schedule

The workflow runs every **Sunday at 2:00 AM UTC** automatically. Any new repos you create during the week will get a README on the next scheduled run.

---

## 🤝 Contributing

Got an idea to make it better? PRs are welcome!

- Add support for other AI providers (OpenAI, Gemini, Ollama)
- Improve tech stack detection
- Add README quality scoring before deciding to regenerate
- Support for org repositories

```bash
git checkout -b feature/your-idea
git commit -m "feat: your idea"
git push origin feature/your-idea
```

---

## 🗺️ Roadmap

- [ ] README quality checker (skip if already good)
- [ ] Support GitHub Organizations
- [ ] Add Ollama support (fully local, zero API)
- [ ] Custom README templates per language
- [ ] Telegram/Discord notification after run

---

## 👤 Author

**Kiran Shams**  
Full Stack Developer & AgriClima AI Consultant

- GitHub: [@kiranShamsHere](https://github.com/kiranShamsHere)
- LinkedIn: [Kiran Shams](https://linkedin.com/in/kiranShamsHere)

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

> ⭐ If this saved you time, star the repo — it helps others find it too!
