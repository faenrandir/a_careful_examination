#!/bin/bash

JEKYLL_ENV=production bundle exec jekyll build

# git add modified
git add -u

# git add untracked
git add $(git ls-files -o --exclude-standard)

git push
