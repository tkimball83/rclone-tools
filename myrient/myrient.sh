#!/usr/bin/env bash
#
# shellcheck disable=SC2220

while getopts "b:c:df:s:t:" opt; do
  case $opt in
    b) rclone_bin=$OPTARG ;;
    c) rclone_config=$OPTARG ;;
    d) rclone_debug=true ;;
    f) rclone_yaml=$OPTARG ;;
    s) rclone_shyaml=$OPTARG ;;
    t) rclone_transfer=$OPTARG ;;
  esac
done

RCLONE_BIN=${rclone_bin-/usr/bin/rclone}
RCLONE_CONFIG=${rclone_config-myrient.conf}
RCLONE_SHYAML=${rclone_shyaml-/usr/bin/shyaml}
RCLONE_TRANSFER=${rclone_transfer-copy}
RCLONE_YAML=${rclone_yaml-myrient.yaml}

for opt in ${RCLONE_BIN} ${RCLONE_CONFIG} ${RCLONE_SHYAML} ${RCLONE_YAML}; do
  if [[ ! -f "${opt}" ]]; then
    echo "ERROR: Unable to locate ${opt}, exiting."
    exit 1
  fi
done

for i in ../lib/*; do
  source "${i}"
done

yaml_length=$(get_length myrient)

if [[ -z "${yaml_length}" ]] || [[ ! "${yaml_length}" -gt 0 ]]; then
  echo "ERROR: The rclone myrient list is empty, exiting."
  exit 1
fi

for i in $(seq 0 $((yaml_length - 1))); do

  declare -A map
  for key in name destination options sources; do
    map[${key}]=$(get_value "myrient.${i}.${key}")
    if [[ -z "${map[${key}]}" ]]; then
      echo "ERROR: Missing key/value pair myrient.${i}.${key}, skipping."
      continue 2
    fi
  done

  if [[ -f "filters/${map['name']}.filter" ]]; then
    map['filter_from']="${map['name']}.filter"
  else
    map['filter_from']="all.filter"
  fi

  map['sources']=$(get_length "myrient.${i}.sources")

  for s in $(seq 0 $((map['sources'] - 1))); do
    map['source']=$(get_value "myrient.${i}.sources.${s}")

    if [[ "${rclone_debug}" = true ]]; then
      echo
      for key in "${!map[@]}"; do
        debug "${key^^} -> ${map[${key}]}"
      done
      echo
    fi

    "${RCLONE_BIN}" mkdir "${map['destination']}"

    # shellcheck disable=SC2086
    "${RCLONE_BIN}" "${RCLONE_TRANSFER}" \
      --config "${RCLONE_CONFIG}" \
      --filter-from "filters/${map['filter_from']}" \
      ${map['options']} \
      "${map['source']}" \
      "${map['destination']}"

  done
done
