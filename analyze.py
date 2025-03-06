import pandas as pd
from datetime import datetime

# Update the environment variable to accept multiple repos
REPO_NAMES = os.getenv("REPO_NAMES", "").split(",")  # Comma-separated list of repos
GITHUB_URL = os.getenv("GITHUB_URL", "http://github.cognizant.com")

def analyze_repos(start_date, end_date):
    """Analyzes commits across multiple repositories."""
    g = Github(
        base_url=f"{GITHUB_URL}/api/v3",
        login_or_token=GITHUB_TOKEN,
        verify=False,
        timeout=30
    )
    
    all_results = {}
    
    for repo_name in REPO_NAMES:
        repo_name = repo_name.strip()  # Remove any whitespace
        print(f"\n📂 Analyzing repository: {repo_name}")
        
        try:
            repo = g.get_repo(repo_name)
            commit_counts = defaultdict(int)
            line_counts = defaultdict(int)
            branch_commits = defaultdict(list)
            
            branches = repo.get_branches()
            print(f"🔍 Found {sum(1 for _ in branches)} branches")
            
            for branch in branches:
                print(f"   📁 Processing branch: {branch.name}")
                try:
                    commits = repo.get_commits(sha=branch.name, since=start_date, until=end_date)
                    for commit in commits:
                        if commit.author:
                            author_email = commit.commit.author.email
                            commit_sha = commit.sha
                            
                            if commit_sha not in branch_commits[author_email]:
                                commit_counts[author_email] += 1
                                branch_commits[author_email].append(commit_sha)
                                
                                try:
                                    stats = commit.stats
                                    total_changes = stats.additions + stats.deletions
                                    line_counts[author_email] += total_changes
                                except Exception as e:
                                    print(f"⚠️ Error getting stats for commit {commit_sha}: {e}")
                                    
                except Exception as e:
                    print(f"⚠️ Error processing branch {branch.name}: {e}")
                    continue
            
            all_results[repo_name] = (commit_counts, line_counts)
            
        except Exception as e:
            print(f"❌ Error processing repository {repo_name}: {e}")
            all_results[repo_name] = ({}, {})
    
    return all_results

def export_to_excel(all_results, start_date, end_date):
    """Exports the analysis results to an Excel file."""
    # Create a list to store all data
    data = []
    
    for repo_name, (commit_counts, line_counts) in all_results.items():
        for author, commits in commit_counts.items():
            data.append({
                'Repository': repo_name,
                'Author': author,
                'Commits': commits,
                'Lines Changed': line_counts[author],
                'Analysis Period': f"{start_date.date()} to {end_date.date()}"
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"commit_analysis_{timestamp}.xlsx"
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Commit Analysis', index=False)
        
        # Auto-adjust columns width
        worksheet = writer.sheets['Commit Analysis']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    return filename

def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub commits across multiple repositories.")
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
        all_results = analyze_repos(start_date, end_date)

        print("\n📊 Commit Analysis Results (CET timezone):")
        print("=" * 50)
        
        # Display results in console
        for repo_name, (commit_counts, line_counts) in all_results.items():
            print(f"\n📂 Repository: {repo_name}")
            print("-" * 40)
            
            if not commit_counts:
                print("No commits found for the given date range.")
                continue
                
            for author, commits in sorted(commit_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"\n👤 User: {author}")
                print(f"   Commits: {commits}")
                print(f"   Lines changed: {line_counts[author]}")
        
        # Export to Excel
        excel_file = export_to_excel(all_results, start_date, end_date)
        print(f"\n✅ Results exported to: {excel_file}")
                
    except Exception as e:
        print(f"❌ Error analyzing commits: {e}")

if __name__ == "__main__":
    main()
