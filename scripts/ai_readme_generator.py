#!/usr/bin/env python3
"""
AI-Powered GitHub README Generator
Scans all repos, analyzes content, and generates unique READMEs using Claude AI
"""

import os
import subprocess
import json
import base64
from pathlib import Path
from typing import Optional, Dict, List
from github import Github, GithubException
from anthropic import Anthropic
import logging
from datetime import datetime

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/readme_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RepoAnalyzer:
    """Analyzes repository content and structure"""
    
    def __init__(self, repo, temp_dir="/tmp/repo_analysis"):
        self.repo = repo
        self.temp_dir = temp_dir
        self.analysis = {}
    
    def get_file_tree(self, max_files=50) -> str:
        """Get repo file structure"""
        try:
            contents = self.repo.get_contents("")
            files = []
            
            def traverse(items, prefix=""):
                count = [0]
                for item in items:
                    if count[0] >= max_files:
                        break
                    if item.type == "dir" and not item.name.startswith('.'):
                        files.append(f"{prefix}📁 {item.name}/")
                    else:
                        ext = Path(item.name).suffix
                        icon = self._get_file_icon(ext)
                        files.append(f"{prefix}{icon} {item.name}")
                    count[0] += 1
            
            traverse(contents)
            return "\n".join(files[:30])
        except Exception as e:
            logger.warning(f"Could not get file tree: {e}")
            return ""
    
    @staticmethod
    def _get_file_icon(ext: str) -> str:
        """Get emoji icon for file type"""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.jsx': '⚛️',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.java': '☕',
            '.cpp': '⚙️',
            '.c': '🔧',
            '.rb': '💎',
            '.go': '🐹',
            '.rs': '🦀',
            '.php': '🐘',
            '.sql': '💾',
            '.sh': '🔨',
            '.yml': '⚙️',
            '.yaml': '⚙️',
        }
        return icons.get(ext, '📄')
    
    def detect_technologies(self) -> List[str]:
        """Detect tech stack from files"""
        techs = []
        try:
            # Check package.json
            try:
                pkg = self.repo.get_contents("package.json")
                data = json.loads(pkg.decoded_content)
                if 'dependencies' in data:
                    deps = data['dependencies']
                    if 'react' in deps or 'react-dom' in deps:
                        techs.append('React')
                    if 'vue' in deps:
                        techs.append('Vue.js')
                    if 'angular' in deps:
                        techs.append('Angular')
                    if 'express' in deps:
                        techs.append('Express')
                    if 'next' in deps:
                        techs.append('Next.js')
                    if 'typescript' in deps or 'ts-node' in deps:
                        techs.append('TypeScript')
                techs.append('Node.js')
            except:
                pass
            
            # Check requirements.txt
            try:
                req = self.repo.get_contents("requirements.txt")
                reqs = req.decoded_content.decode().split('\n')
                if any('django' in r for r in reqs):
                    techs.append('Django')
                if any('flask' in r for r in reqs):
                    techs.append('Flask')
                techs.append('Python')
            except:
                pass
            
            # Check file types
            try:
                contents = self.repo.get_contents("")
                for item in contents:
                    if item.name.endswith('.html'):
                        techs.append('HTML')
                    if item.name.endswith('.css'):
                        techs.append('CSS')
                    if item.name.endswith('.java'):
                        techs.append('Java')
                    if item.name.endswith('.go'):
                        techs.append('Go')
                    if item.name.endswith('.rs'):
                        techs.append('Rust')
            except:
                pass
            
            # Remove duplicates
            return list(set(techs)) if techs else ['JavaScript', 'Web']
        
        except Exception as e:
            logger.warning(f"Error detecting technologies: {e}")
            return ['Web Development']
    
    def get_repo_stats(self) -> Dict:
        """Get repository statistics"""
        try:
            return {
                'language': self.repo.language or 'Unknown',
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count,
                'watchers': self.repo.watchers_count,
                'topics': self.repo.topics,
            }
        except:
            return {}
    
    def analyze(self) -> Dict:
        """Perform full analysis"""
        logger.info(f"Analyzing {self.repo.name}...")
        
        self.analysis = {
            'name': self.repo.name,
            'description': self.repo.description or "A project by kiranShamsHere",
            'url': self.repo.html_url,
            'file_tree': self.get_file_tree(),
            'technologies': self.detect_technologies(),
            'stats': self.get_repo_stats(),
            'is_fork': self.repo.fork,
            'has_wiki': self.repo.has_wiki,
        }
        
        return self.analysis


class AIReadmeGenerator:
    """Generates READMEs using Claude AI"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate(self, analysis: Dict) -> str:
        """Generate README using AI"""
        logger.info(f"Generating README for {analysis['name']} with AI...")
        
        prompt = f"""You are an expert technical writer and developer. Create a comprehensive, professional, and engaging GitHub README.md for this project.

PROJECT ANALYSIS:
- Name: {analysis['name']}
- Description: {analysis['description']}
- Primary Language: {analysis['stats'].get('language', 'Unknown')}
- Technologies: {', '.join(analysis['technologies'])}
- Topics: {', '.join(analysis['stats'].get('topics', []))}
- Is Fork: {analysis['is_fork']}

FILE STRUCTURE:
{analysis['file_tree']}

REQUIREMENTS:
1. Create an original, unique README that matches this specific project
2. Include these sections in order:
   - 📋 Project Title and Description
   - ✨ Features (list 3-5 relevant features based on project type)
   - 🛠️ Technologies & Tools Used
   - 📂 Project Structure
   - 🚀 Getting Started (Prerequisites & Installation)
   - 💻 Usage/How to Use
   - 🤝 Contributing
   - 📄 License
   - 👤 Author (kiranShamsHere)

3. Writing style:
   - Professional but friendly
   - Use relevant emojis
   - Clear code examples where applicable
   - Make it beginner-friendly

4. Make the README:
   - Unique to THIS specific project (not generic)
   - Approximately 200-400 lines
   - Include practical examples
   - SEO-friendly with good formatting

5. Format:
   - Use proper Markdown syntax
   - Include code blocks with language specification
   - Use tables for comparison/features where relevant
   - Add badges if appropriate (e.g., language, license)

Generate ONLY the README.md content, no additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        readme_content = message.content[0].text
        logger.info(f"✅ README generated for {analysis['name']}")
        return readme_content


class GitHubReadmeManager:
    """Manages README creation in GitHub"""
    
    def __init__(self, gh_token: str):
        self.gh = Github(gh_token)
        self.user = self.gh.get_user()
    
    def readme_exists(self, repo) -> bool:
        """Check if README exists"""
        try:
            repo.get_contents("README.md")
            return True
        except GithubException:
            return False
    
    def commit_readme(self, repo, content: str) -> bool:
        """Commit README to repository"""
        try:
            logger.info(f"Committing README to {repo.name}...")
            
            repo.create_file(
                path='README.md',
                message='docs: 📝 Generate AI-powered README',
                content=content,
                branch=repo.default_branch
            )
            
            logger.info(f"✅ Successfully created README in {repo.name}")
            return True
        
        except GithubException as e:
            logger.error(f"Failed to commit to {repo.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error committing to {repo.name}: {e}")
            return False
    
    def process_all_repos(self, force_regenerate: bool = False):
        """Process all user repositories"""
        logger.info("=" * 60)
        logger.info("🚀 Starting AI README Generator")
        logger.info("=" * 60)
        
        repos = self.user.get_repos(sort='updated', direction='desc')
        stats = {
            'total': 0,
            'processed': 0,
            'skipped': 0,
            'created': 0,
            'errors': 0,
        }
        
        for repo in repos:
            stats['total'] += 1
            
            try:
                # Skip forked repos if they have README
                if repo.fork and self.readme_exists(repo):
                    logger.info(f"⏭️ Skipping fork {repo.name} (has README)")
                    stats['skipped'] += 1
                    continue
                
                # Check if README exists
                if self.readme_exists(repo) and not force_regenerate:
                    logger.info(f"⏭️ Skipping {repo.name} (README exists)")
                    stats['skipped'] += 1
                    continue
                
                # Skip archived repos
                if repo.archived:
                    logger.info(f"⏭️ Skipping {repo.name} (archived)")
                    stats['skipped'] += 1
                    continue
                
                # Analyze repository
                analyzer = RepoAnalyzer(repo)
                analysis = analyzer.analyze()
                
                # Generate README with AI
                generator = AIReadmeGenerator(os.environ['ANTHROPIC_API_KEY'])
                readme_content = generator.generate(analysis)
                
                # Commit README
                if self.commit_readme(repo, readme_content):
                    stats['created'] += 1
                else:
                    stats['errors'] += 1
                
                stats['processed'] += 1
            
            except Exception as e:
                logger.error(f"Error processing {repo.name}: {e}")
                stats['errors'] += 1
        
        # Print summary
        self._print_summary(stats)
    
    def _print_summary(self, stats: Dict):
        """Print workflow summary"""
        logger.info("=" * 60)
        logger.info("📊 README Generation Summary")
        logger.info("=" * 60)
        logger.info(f"Total repositories scanned: {stats['total']}")
        logger.info(f"Processed: {stats['processed']}")
        logger.info(f"READMEs created: {stats['created']} ✅")
        logger.info(f"Skipped (existing/archived): {stats['skipped']}")
        logger.info(f"Errors: {stats['errors']} ❌")
        logger.info("=" * 60)


def main():
    """Main execution"""
    gh_token = os.environ.get('GH_TOKEN')
    ai_key = os.environ.get('ANTHROPIC_API_KEY')
    force_regenerate = os.environ.get('FORCE_REGENERATE', 'false').lower() == 'true'
    
    if not gh_token:
        logger.error("❌ GH_TOKEN not set")
        return
    
    if not ai_key:
        logger.error("❌ ANTHROPIC_API_KEY not set")
        return
    
    logger.info(f"Force Regenerate: {force_regenerate}")
    
    manager = GitHubReadmeManager(gh_token)
    manager.process_all_repos(force_regenerate=force_regenerate)


if __name__ == '__main__':
    main()