#!/bin/bash

# ensure that there are no outstanding commits that are missing
git pull

JEKYLL_ENV=production bundle exec jekyll build

# git add modified
git add -u

# git add untracked
git add $(git ls-files -o --exclude-standard)

git commit -m "new or modified"

git push
