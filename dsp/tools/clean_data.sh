#!/bin/sh

# this doesn't super work well, but does more or less what it needs to do.

find "$1" -maxdepth 4 -type f | while IFS= read -r file; do
    rename 's/bad_takamine_//' "$file"
    rename 's/\s[0-9]*//' "$file"
    rename 's/\(*[0-9]*\)//' "$file"
done