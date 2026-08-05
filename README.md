# A Careful Examination: researching LDS truth-claims and thinking

See [About](https://faenrandir.github.io/a_careful_examination/about/)

## To Build

The site is built with [Zola](https://www.getzola.org/). Make sure `zola` is
installed and in your PATH, then navigate into the root folder of this project.

Preview changes (serves locally with live reload):

    zola serve

Build the site (outputs static files to `docs/`):

    zola build

Release (switches to the release git user, pulls latest, rebuilds, commits,
and pushes):

    python3 scripts/release.py


## LICENSE

Code is under MIT license and all content produced by faenrandir is under a
CC0 license.  The copyright to copies of content produced by others is held by
them.  See LICENSE for details.
