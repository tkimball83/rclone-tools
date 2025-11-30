#!/usr/bin/env bash

function get_value() {
  local key="${1}"
  local query
  local value

  query=$(get_type "${key}")

  if [[ -z "${query}" ]]; then
    value=
  else
    value=$("${RCLONE_SHYAML}" "${query}" "${key}" <"${RCLONE_YAML}" | tr '\n' ' ' 2>/dev/null)
  fi

  echo "${value}"
}
