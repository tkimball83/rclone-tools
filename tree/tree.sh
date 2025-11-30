#!/usr/bin/env bash

while getopts "b:c:df:s:t:" opt; do
  case $opt in
    b) rclone_bin=$OPTARG ;;
    c) rclone_config=$OPTARG ;;
    d) rclone_dryrun=true ;;
    f) rclone_yaml=$OPTARG ;;
    s) rclone_shyaml=$OPTARG ;;
    t) rclone_transfer=$OPTARG ;;
  esac
done

RCLONE_BIN=${rclone_bin-/usr/bin/rclone}
RCLONE_CONFIG=${rclone_config-/etc/rclone/rclone.conf}
RCLONE_SHYAML=${rclone_shyaml-/usr/bin/shyaml}
RCLONE_TRANSFER=${rclone_transfer-sync}
RCLONE_YAML=${rclone_yaml-tree.yaml}

for opt in ${RCLONE_BIN} ${RCLONE_CONFIG} ${RCLONE_SHYAML} ${RCLONE_YAML}; do
  if [[ ! -f "${opt}" ]]; then
    echo "ERROR: Unable to locate ${opt}, exiting."
    exit 1
  fi
done

for i in ../lib/*; do
  source "${i}"
done

tree_length=$(get_length tree)

if [[ -z "${tree_length}" ]] || [[ ! "${tree_length}" -gt 0 ]]; then
  echo "ERROR: The rclone tree list is empty, exiting."
  exit 1
fi

for t in $(seq 0 $((tree_length - 1))); do

  trunk=$(get_value "tree.${t}.trunk")
  branch_length=$(get_length "tree.${t}.branches")

  if [[ -z "${branch_length}" ]] || [[ ! "${branch_length}" -gt 0 ]]; then
    echo "WARNING: The rclone tree has no branches, skipping."
    continue
  fi

  for b in $(seq 0 $((branch_length -1))); do

    branch=$(get_value "tree.${t}.branches.${b}.name")
    leaf_length=$(get_length "tree.${t}.branches.${b}.leafs")

    if [[ -z "${branch}" ]]; then
      echo "WARNING: the rclone branch has no name, skipping."
      continue
    fi

    if [[ -z "${leaf_length}" ]] || [[ ! "${leaf_length}" -gt 0 ]]; then
      echo "WARNING: The rclone branch has no leafs, skipping."
      continue
    fi

    for l in $(seq 0 $((leaf_length - 1))); do
      leaf=$(get_value "tree.${t}.branches.${b}.leafs.${l}")

      echo -e "\n[*]: ${trunk}:${leaf} -> ${branch}:${leaf}\n"

      if [[ "${rclone_dryrun}" = true ]]; then
        ${RCLONE_BIN} ${RCLONE_TRANSFER} --dry-run ${trunk}:${leaf} ${branch}:${leaf}
      else
        ${RCLONE_BIN} ${RCLONE_TRANSFER} ${trunk}:${leaf} ${branch}:${leaf}
      fi

    done
  done
done
