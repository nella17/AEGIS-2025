#!/bin/bash
set -ex
diff -s <(./sla.py) <(./sla.py BINARY=$1)
