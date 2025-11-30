#!/usr/bin/env bash

function get_length() {
  local key="${1}"
  local length

  length=$("${RCLONE_SHYAML}" get-length "${key}" <"${RCLONE_YAML}" 2>/dev/null)

  echo "${length}"
}
