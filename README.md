# rclone-tree

[![License](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](#license)

A YAML-controlled bash script to sync between multiple rclone remotes.

## Requirements

| Requirement                                | Description               |
| ------------------------------------------ | ------------------------- |
| [rclone](https://github.com/rclone/rclone) | rsync for cloud storage   |
| [shyaml](https://github.com/0k/shyaml)     | YAML for the command line |

## Usage

    bash tree.sh [options]

## Options

| Flag | Default                   | Description                         |
| ---- | ------------------------- | ----------------------------------- |
| `-b` | `rclone`                  | Change path to rclone binary        |
| `-c` | `null`                    | Change path to rclone config        |
| `-d` | `false`                   | Enable dry run and command output   |
| `-f` | `tree.yaml`               | Change path to script config YAML   |
| `-k` | `8`                       | Change rclone checkers setting      |
| `-l` | `0`                       | Change rclone bandwidth limit       |
| `-s` | `shyaml`                  | Change path to shyaml binary        |
| `-t` | `4`                       | Change rclone transfers setting     |

If `-c` is not provided, the script uses the first existing config at:
`~/.config/rclone/rclone.conf`, then `/etc/rclone/rclone.conf`.

## Examples

    bash tree.sh -d
    bash tree.sh -k 16
    bash tree.sh -l 100M
    bash tree.sh -b ~/.local/bin/rclone -c ~/.config/rclone/rclone.conf
    bash tree.sh -s /opt/homebrew/bin/shyaml

## License

Copyright (c) Taylor Kimball

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
