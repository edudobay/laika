#!/usr/bin/env bash

set -o nounset -o pipefail -o errexit

source_hooks_dir=$(dirname "$0")
target_hooks_dir=.git/hooks

for source_file in $(ls "$source_hooks_dir"/*.hook)
do
  hook=$(basename "$source_file" .hook)
  target_file=$target_hooks_dir/$hook
  source_file=$(readlink -f "$source_file")
  existing_link_target=$(readlink -e "$target_file" || true)

  if [[ -L "$target_file" || -e "$target_file" ]]; then
    if [ "$existing_link_target" = "$source_file" ]; then
      continue
    elif [[ ! -L "$target_file" ]]; then
      new_name=${target_file}.backup_$(date +%s)
      echo "info: $target_file exists; renaming to $(basename "$new_name")"
      mv -n "$target_file" "$new_name"
    fi
  fi

  echo "info: installing hook $target_file"
	ln -s "$(realpath --relative-to="$target_hooks_dir" "$source_file")" "$target_file"
done

echo "info: git hooks up to date"
