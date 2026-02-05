# tree

[![License](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](COPYING)

A yaml controlled bash script to sync between multiple rclone remotes

## Usage

    bash tree.sh [options]

## Options

| Flag | Default                   | Description                         |
| ---- | ------------------------- | ----------------------------------- |
| `-b` | `/usr/bin/rclone`         | Change path to rclone binary        |
| `-c` | `/etc/rclone/rclone.conf` | Change path to rclone config        |
| `-d` | `false`                   | Enable dry run execution            |
| `-f` | `tree.yaml`               | Change path to script config yaml   |
| `-s` | `/usr/bin/shyaml`         | Change path to shyaml binary        |
| `-t` | `4`                       | Change rclone transfers setting     |

## Examples

    bash tree.sh -d
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
