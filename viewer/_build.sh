#!/usr/bin/bash

# IMPORTANT USAGE ABOUT THIS CRUMMY BUILD SCRIPT:
# - Run it once so that it detects there are changes --> it will use the CURRENT git hash,
#   update src/GitBuild.tsx accordingly, and complain git status isn't clean (duh, it changed a file).
# - That's on purpose because the whole point is to do a git commit first, but obviously I'd have
#   forgotten to do, so it acts as a warning.
#   So just run it again, capturing the git hash every time.
# - It only updates VERSION_MINOR once. If modified, it is not modified any further.
# - Once satisfied that the git hash does actually match a commit, run again with -y.
#   That time, it won't check the git status and will actually perform a build.
# - On the outset, you'll ALWAYS end up with (ideally) just one change in src/GitBuild.tsx.
#   Just commit that with a git tag "viewer_x.y" matching the version number.

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

if [[ "$1" != "-y" ]]; then
  if ! git show HEAD | grep -q "VERSION_MINOR =" ; then
    VERSION_MINOR=$((VERSION_MINOR + 1))
  fi

  cat <<EOL >src/GitBuild.tsx
export const GIT_HASH_STR = "$GIT_HASH";
export const GIT_LONG_STR = "$GIT_LONG";
export const VERSION_MAJOR = "$VERSION_MAJOR";
export const VERSION_MINOR = "$VERSION_MINOR";
EOL

  if [[ -n $(git status -s) ]]; then
    echo "ERROR: Git working tree is dirty. There are modified and/or untracked files. Commit or stash first."
    echo
    git status
    echo
    echo src/GitBuild.tsx:
    cat src/GitBuild.tsx
    echo
    echo "ERROR: Git working tree is dirty. There are modified and/or untracked files. Commit or stash first,"
    echo "then use -y to override this check (since this will necessarily modify src/GitBuild.tsx)."
    exit 1
  fi
fi

echo src/GitBuild.tsx:
cat src/GitBuild.tsx

npm run build

echo
echo "Suggestion: $ git tag viewer${VERSION_MAJOR}.${VERSION_MINOR}"
