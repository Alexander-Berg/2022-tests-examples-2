#!/bin/sh
mergeCommitTitle=$(arc log --max-count=1 --pretty=format:%B)

npx testcop-cli enable --projects "home" --branch "trunk" --merge-commit-title "$mergeCommitTitle"
