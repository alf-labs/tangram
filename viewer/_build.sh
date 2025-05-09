#!/usr/bin/bash

EXPECT=24
NODE_MAJ=$(node --version | tr -d v | cut -d . -f 1)

if [[ "NODE_MAJ" -lt "$EXPECT" ]]; then
  echo "Expecting node.js version v$EXPECT or higher, but was $NODE_MAJ."
  exit 1
fi

# Git branch that works with my older 2.21 git-bash-win
# Starting with 2.22, I have "git branch --show-current"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

GIT_HASH=$(git log --format="$GIT_BRANCH @ %h" -n 1 HEAD)
GIT_LONG=$(git log --format="Build $GIT_BRANCH @ %h, %ci" -n 1 HEAD)

VERSION_MAJOR=$(grep VERSION_MAJOR src/GitBuild.tsx | cut -d \" -f 2)
VERSION_MINOR=$(grep VERSION_MINOR src/GitBuild.tsx | cut -d \" -f 2)
VERSION_MINOR=$((VERSION_MINOR + 1))

cat <<EOL >src/GitBuild.tsx
export const GIT_HASH_STR = "$GIT_HASH";
export const GIT_LONG_STR = "$GIT_LONG";
export const VERSION_MAJOR = "$VERSION_MAJOR";
export const VERSION_MINOR = "$VERSION_MINOR";
EOL

if [[ "$1" != "-y" ]]; then
  if [[ -n $(git status -s) ]]; then
    echo "ERROR: Git working tree is dirty. There are modified and/or untracked files. Commit or stash first."
    echo
    git status
    echo
    echo "ERROR: Git working tree is dirty. There are modified and/or untracked files. Commit or stash first,"
    echo "then use -y to override this check (since this will necessarily modify src/GitBuild.tsx)."
    exit 1
  fi
fi

npm run build
