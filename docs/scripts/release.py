#!/usr/bin/env python

import subprocess


def run(cmd: str):
    subprocess.run(cmd, shell=True, text=True)


run("gh auth switch --hostname github.com --user faenrandir")

# ensure that there are no outstanding commits that are missing
run("git pull")

run("JEKYLL_ENV=production bundle exec jekyll build")

# git add modified
run("git add -u")

# git add untracked
run("git add $(git ls-files -o --exclude-standard)")

run("git commit -m 'new or modified'")

run("git push")


run("gh auth switch --hostname github.com --user jtprince")
