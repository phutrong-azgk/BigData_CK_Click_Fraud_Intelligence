#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="/app/data/raw/train_sample.csv"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Missing dataset: $INPUT_FILE"
  echo "Download train_sample.csv from Kaggle and place it in data/raw/."
  exit 1
fi

rm -rf /app/output/real_ip_risk /app/output/hourly_stats

pig -x local /app/pig/03_real_data_risk.pig

test -f /app/output/real_ip_risk/part-r-00000
test -f /app/output/hourly_stats/part-r-00000

