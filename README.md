# GitHub Commit Analysis Tool

This tool analyzes GitHub commits within a specified date range, providing statistics about commit counts and lines of code changed per user.

## Prerequisites

- Python 3.6 or higher
- Git
- A GitHub personal access token

## GitHub Token Creation

1. Go to GitHub.com and sign in to your account
2. Click your profile icon > Settings
3. Scroll down to Developer settings (bottom of left sidebar)
4. Select Personal access tokens > Tokens (classic)
5. Click "Generate new token" > "Generate new token (classic)"
6. Name your token in the "Note" field
7. For Public Repositories:
- Select 'repo:read' for reading repository data
- For private repositories, select 'repo' for full read access
- For commit and code stats, select:
    - 'repo:status'
    - 'read:org' (if working with an organization)
    - 'read:user' (if working with user data)
    - 'user:email' (for email addresses)
    - 'read:enterprise' (for enterprise accounts)
8. Click "Generate token" and copy the token to a secure location

## Installation

1. Clone the repository and create a virtual environment:
```bash
git clone <repository-url>
cd <repository-name>
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install required packages:
```bash
pip install PyGithub python-dotenv pytz
```

3. Create a `.env` file in the root directory:
```properties
GITHUB_TOKEN = "your_github_token_here"  # Replace with your GitHub personal access token
REPO_NAME = "owner/repository"           # Format: username/repository-name
```

## Usage

The script can be run in two modes:

1. Analyze yesterday's commits:
```bash
python calc.py
```

2. Analyze commits for a specific date range:
```bash
python calc.py --start_date 2023-01-01 --end_date 2023-01-31
```

## Output

The script will display:
- Number of commits per user
- Lines of code changed per user
- All times are in CET timezone

## Error Handling

The script includes error handling for:
- Invalid date formats
- GitHub API errors
- Repository access issues

## Notes

- Ensure your GitHub token has appropriate permissions to access the repository
- All dates should be in YYYY-MM-DD format
- The script uses CET timezone for calculations
