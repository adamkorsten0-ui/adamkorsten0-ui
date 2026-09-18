import json
import re
import urllib.request
from datetime import datetime, timezone

USERNAME = "adamkorsten0-ui"
API_URL = f"https://api.github.com/users/{USERNAME}/events/public"

def fetch_activity():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "GitHub-Action"})
    try:
        with urllib.request.urlopen(req) as resp:
            events = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Notice: Could not fetch events: {e}")
        return ["- *Exploring new code and open source projects.*"]

    activities = []
    for ev in events:
        if len(activities) >= 5:
            break
        ev_type = ev.get("type")
        repo = ev.get("repo", {}).get("name", "")
        repo_url = f"https://github.com/{repo}"
        
        if ev_type == "PushEvent":
            commits = ev.get("payload", {}).get("commits", [])
            count = len(commits)
            activities.append(f"- 🔨 Pushed {count} commit(s) to [{repo}]({repo_url})")
        elif ev_type == "CreateEvent":
            ref_type = ev.get("payload", {}).get("ref_type", "repo")
            activities.append(f"- 📦 Created {ref_type} in [{repo}]({repo_url})")
        elif ev_type == "WatchEvent":
            activities.append(f"- ⭐ Starred [{repo}]({repo_url})")
        elif ev_type == "PullRequestEvent":
            action = ev.get("payload", {}).get("action", "opened")
            activities.append(f"- 🔀 {action.capitalize()} pull request in [{repo}]({repo_url})")

    if not activities:
        activities.append("- *Exploring new code and open source projects.*")
    return activities

def update_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = f"# {USERNAME}\n\n"

    activities = fetch_activity()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    activity_block = "\n".join(activities)
    new_section = (
        "<!-- START_ACTIVITY -->\n"
        "### ⚡ Recent GitHub Activity\n"
        f"{activity_block}\n\n"
        f"*(Last updated: {now})*\n"
        "<!-- END_ACTIVITY -->"
    )

    pattern = r"<!-- START_ACTIVITY -->.*?<!-- END_ACTIVITY -->"
    if re.search(pattern, content, flags=re.DOTALL):
        updated = re.sub(pattern, new_section, content, flags=re.DOTALL)
    else:
        updated = content.rstrip() + "\n\n" + new_section + "\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README.md updated successfully.")

if __name__ == "__main__":
    update_readme()
