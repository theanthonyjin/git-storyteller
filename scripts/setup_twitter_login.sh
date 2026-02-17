#!/bin/bash
# Setup script for git-storyteller Twitter login

echo "🌐 Opening Chrome for Twitter login setup..."
echo ""
echo "1. Chrome will open with the git-storyteller profile"
echo "2. Log into Twitter/X"
echo "3. Once logged in, close Chrome"
echo "4. Then run: python scripts/analyze_and_tweet.py --confirm"
echo ""

# Open Chrome with the git-storyteller profile and navigate to Twitter
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir=/tmp/git-storyteller-chrome-profile \
  --no-first-run \
  --no-default-browser-check \
  "https://twitter.com" &
