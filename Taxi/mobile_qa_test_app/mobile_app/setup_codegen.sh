cd .dart_tool
mkdir -p flutter_gen
cd flutter_gen
rm -f pubspec.yaml
echo "
name: test
description: A new Flutter application.
version: 1.0.0

dependencies:

dev_dependencies:
" >> pubspec.yaml