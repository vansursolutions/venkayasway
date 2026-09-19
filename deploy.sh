#!/bin/sh
# Publish www/ to GitHub Pages (gh-pages branch). Run after committing changes on main.
set -e
cd "$(dirname "$0")"
git push origin main
git subtree split --prefix www -b gh-pages-tmp >/dev/null
git push -f origin gh-pages-tmp:gh-pages
git branch -D gh-pages-tmp >/dev/null
echo "Published. Live in ~1 minute."
