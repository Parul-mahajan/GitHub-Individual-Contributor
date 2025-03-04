import os
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import pytz
from github import Github
from dotenv import load_dotenv
import urllib3
import ssl

# Load environment variables from .env file
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
GITHUB_URL = os.getenv("GITHUB_URL", "http://github.cognizant.com") 

def get_yesterday_range():
    """Returns start and end timestamps for yesterday in CET timezone."""
    cet = pytz.timezone('CET')
    now = datetime.now(cet)
    yesterday = now - timedelta(days=1)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_date, end_date

def get_custom_range(start_date_str, end_date_str):
    """Parses the provided date strings and returns start and end timestamps in CET timezone."""
    cet = pytz.timezone('CET')
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        start_date = cet.localize(start_date.replace(hour=0, minute=0, second=0, microsecond=0))
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        end_date = cet.localize(end_date.replace(hour=23, minute=59, second=59, microsecond=999999))
        return start_date, end_date
    except Exception as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD. Error: {e}")

def analyze_commits(start_date, end_date):
    """Fetches commits from the given repository within the provided date range and calculates per-user stats."""
    g = Github(
        base_url=f"{GITHUB_URL}/api/v3",
        login_or_token=GITHUB_TOKEN,
        verify=False,
        timeout=30
    )
    
    try:
        repo = g.get_repo(REPO_NAME)  # Format: "owner/repo"
        commit_counts = defaultdict(int)
        line_counts = defaultdict(int)
        
        commits = repo.get_commits(since=start_date, until=end_date)
        for commit in commits:
            if commit.author:  # Ensure commit has an author
                author_email = commit.commit.author.email
                commit_counts[author_email] += 1

                # Count lines changed (additions + deletions)
                try:
                    stats = commit.stats
                    total_changes = stats.additions + stats.deletions
                    line_counts[author_email] += total_changes
                except Exception as e:
                    print(f"⚠️ Error getting stats for commit {commit.sha} in {REPO_NAME}: {e}")

        return commit_counts, line_counts

    except Exception as e:
        print(f"❌ Error processing repository {REPO_NAME}: {e}")
        return {}, {}

def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub commits within a date range.")
    parser.add_argument("--start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=str, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    if args.start_date and args.end_date:
        try:
            start_date, end_date = get_custom_range(args.start_date, args.end_date)
        except ValueError as ve:
            print(f"❌ {ve}")
            return
    else:
        start_date, end_date = get_yesterday_range()

    try:
        commit_counts, line_counts = analyze_commits(start_date, end_date)

        print("\n📊 Commit Analysis Results (CET timezone):")
        print("=" * 50)
        if not commit_counts:
            print("No commits found for the given repository and date range.")
        else:
            for author, count in sorted(commit_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"\n👤 User: {author}")
                print(f"   📝 Number of commits: {commit_counts[author]}")
                print(f"   📈 Lines of code changed: {line_counts[author]}")
            
    except Exception as e:
        print(f"❌ Error during commit analysis: {e}")

if __name__ == "__main__":
    main()
