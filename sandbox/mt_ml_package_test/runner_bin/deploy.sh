#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

arc_root="$(ya dump root)"
cur_dir="$(pwd)"

prog_name="$(head -n1 ya.make | grep -oE "PROGRAM\(.+\)" | sed -E 's/PROGRAM\((.+)\)/\1/' || true)"
if [[ -z "$prog_name" ]]; then
    prog_name="$(echo "$cur_dir" | rev | cut -d '/' -f1 | rev)"
fi

resource_name="ARCADIA_PROJECT"
if [[ -f artefact.txt ]]; then
    resource_name="$(cat artefact.txt)"
fi

cd "$arc_root/dict/mt/tools/sb_build_program"
if [[ ! -f sb_build_program ]]; then
    echo "===> Build Sandbox launcher"
    ya make -r
fi

echo "===> Start Sandbox task"
build_out="$(./sb_build_program "$cur_dir" "$resource_name" --artefact-name "$prog_name" --build-type relwithdebinfo)"
task_id="$(grep -oE 'Task ID: [0-9]+' <<< "$build_out" | grep -oE '[0-9]+')"

echo "===> Wait for task"
ya tool sandboxctl get_task --wait "$task_id"

echo "===> Deploy note"
echo "Task is finished. Now go to Sandbox and release artifact"
echo "Task link: https://sandbox.yandex-team.ru/task/$task_id/view"
