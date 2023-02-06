export PROJECT_NAME=webview

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')

$ROOT_DIR/tools/command/e2e/run/sync-qyp.sh
