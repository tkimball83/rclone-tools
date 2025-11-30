#!/usr/bin/env bash

function get_type() {
  local key="${1}"
  local query
  local type

  type=$("${RCLONE_SHYAML}" get-type "${key}" <"${RCLONE_YAML}" 2>/dev/null)

  if [[ "${type}" == 'str' ]]; then
    query=get-value
  elif [[ "${type}" == 'sequence' ]]; then
    query=get-values
  else
    query=
  fi

  echo "${query}"
}
