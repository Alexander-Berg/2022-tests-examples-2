import logging
import os

import yatest
from mock import patch

from sandbox.projects.oko.crawl_repositories.packages import PackageExtractor

# package-lock.json RTFM
# https://docs.npmjs.com/cli/v7/configuring-npm/package-lock-json#lockfileversion
#
# tl;dr
# no version: either shrinkwrap or npm before v5
# v1: npm v5, v6
# v2: npm v7 with _backwards_ compatibility to v1 lockfiles
# v3: currently internal npm v7 lockfile in node_modules/.package-lock.json


logger = logging.getLogger("test_logger")
test_dir = yatest.common.source_path('sandbox/projects/oko/crawl_repositories/tests')
package_lock_packages = {
    "enhanced-resolve": "5.8.2",
    "browserslist": "4.17.0",
    "@types/eslint": "7.28.0",
    "merge-stream": "2.0.0",
    "js-tokens": "4.0.0",
    "schema-utils": "3.1.1",
    "colorette": "1.4.0",
    "graceful-fs": "4.2.8",
    "json-parse-better-errors": "1.0.2",
    "commander": "2.20.3",
    "@webassemblyjs/helper-api-error": "1.11.1",
    "terser": "5.8.0",
    "@types/json-schema": "7.0.9",
    "escalade": "3.1.1",
    "punycode": "2.1.1",
    "@webassemblyjs/floating-point-hex-parser": "1.11.1",
    "@webassemblyjs/wasm-gen": "1.11.1",
    "@webassemblyjs/wasm-edit": "1.11.1",
    "tapable": "2.2.1",
    "yocto-queue": "0.1.0",
    "source-map-support": "0.5.20",
    "@webassemblyjs/helper-wasm-section": "1.11.1",
    "@webassemblyjs/utf8": "1.11.1",
    "acorn-import-assertions": "1.7.6",
    "buffer-from": "1.1.2",
    "@webassemblyjs/wasm-opt": "1.11.1",
    "ajv": "6.12.6",
    "@webassemblyjs/helper-buffer": "1.11.1",
    "@types/eslint-scope": "3.7.1",
    "webpack": "5.52.1",
    "@xtuc/long": "4.2.2",
    "eslint-scope": "5.1.1",
    "loose-envify": "1.4.0",
    "caniuse-lite": "1.0.30001257",
    "@webassemblyjs/ieee754": "1.11.1",
    "es-module-lexer": "0.7.1",
    "mime-db": "1.49.0",
    "events": "3.3.0",
    "source-map": "0.6.1",
    "p-limit": "3.1.0",
    "jest-worker": "27.2.0",
    "json-schema-traverse": "0.4.1",
    "safe-buffer": "5.2.1",
    "electron-to-chromium": "1.3.838",
    "supports-color": "8.1.1",
    "estraverse": "4.3.0",
    "randombytes": "2.1.0",
    "react": "17.0.2",
    "webpack-sources": "3.2.1",
    "ajv-keywords": "3.5.2",
    "@webassemblyjs/wast-printer": "1.11.1",
    "@webassemblyjs/ast": "1.11.1",
    "acorn": "8.5.0",
    "@types/node": "16.9.1",
    "@xtuc/ieee754": "1.2.0",
    "fast-json-stable-stringify": "2.1.0",
    "@types/estree": "0.0.50",
    "@webassemblyjs/wasm-parser": "1.11.1",
    "neo-async": "2.6.2",
    "@webassemblyjs/helper-numbers": "1.11.1",
    "mime-types": "2.1.32",
    "serialize-javascript": "6.0.0",
    "uri-js": "4.4.1",
    "watchpack": "2.2.0",
    "fast-deep-equal": "3.1.3",
    "chrome-trace-event": "1.0.3",
    "terser-webpack-plugin": "5.2.4",
    "@webassemblyjs/leb128": "1.11.1",
    "esrecurse": "4.3.0",
    "object-assign": "4.1.1",
    "glob-to-regexp": "0.4.1",
    "loader-runner": "4.2.0",
    "@webassemblyjs/helper-wasm-bytecode": "1.11.1",
    "has-flag": "4.0.0",
    "node-releases": "1.1.75"
}


def test_parse_package_lock_v1():
    with open(os.path.join(test_dir, 'v1', 'package-lock.json'), 'r') as lock_file:
        data = lock_file.read()
    res = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data
    })
    assert res == package_lock_packages


def test_parse_package_lock_v2():
    with open(os.path.join(test_dir, 'v2', 'package-lock.json'), 'r') as lock_file:
        data = lock_file.read()
    res = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data
    })
    assert res == package_lock_packages


def test_parse_package_lock_v3():
    with open(os.path.join(test_dir, 'v3', 'package-lock.json'), 'r') as lock_file:
        data = lock_file.read()
    res = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data
    })
    assert res == {}


def test_parse_package_lock_yarn():
    with open(os.path.join(test_dir, 'yarn', 'yarn.lock'), 'r') as lock_file:
        data = lock_file.read()
    res = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data,
        "lock_variant": "yarn.lock",
    })
    assert res == package_lock_packages


def test_parse_package_lock_yarn_hard():
    with open(os.path.join(test_dir, 'yarn-2', 'yarn.lock'), 'r') as lock_file:
        data = lock_file.read()
    res_yarn = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data,
        "lock_variant": "yarn.lock",
    })

    with open(os.path.join(test_dir, 'yarn-2', 'yarn-with-npm.lock'), 'r') as lock_file:
        data = lock_file.read()
    res_yarn_with_npm = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data,
        "lock_variant": "yarn.lock",
    })

    with open(os.path.join(test_dir, 'yarn-2', 'package-lock.json'), 'r') as lock_file:
        data = lock_file.read()
    res_npm = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data,
        "lock_variant": "package-lock.json",
    })

    assert res_npm == res_yarn
    assert res_yarn == res_yarn_with_npm


def test_parse_package_lock_yarn_weird_fields():
    with open(os.path.join(test_dir, 'yarn-3', 'yarn.lock'), 'r') as lock_file:
        data = lock_file.read()
    res = PackageExtractor._parse_package_lock({
        "project": "A",
        "url": "B",
        "lock_file": data,
        "lock_variant": "yarn.lock",
    })

    assert res == {
        "edadeal-protobuf": "0.1.91655"
    }


extract_versions_data = {
    "url": "A",
    "project": "B",
    "last_commit_time": "C",
    "vcs_type": "D",
    "path": "E",
}
extract_versions_output = {
    "url": "A",
    "project": "B",
    "last_commit_time": "C",
    "vcs_type": "D",
    "path": "E",
    "file_version": "1.0.0",
    "is_deprecated": False,
    "dev_deps": {
        "webpack": "^5.50.0"
    },
    "deps": {
        "react": "^17.0.2"
    },
    "package_lock": package_lock_packages,
    "lock_variant": "package-lock.json",
}


def test_extract_versions_v1():
    with open(os.path.join(test_dir, 'v1', 'package.json'), 'r') as lock_file:
        package_data = lock_file.read()
    with open(os.path.join(test_dir, 'v1', 'package-lock.json'), 'r') as lock_file:
        package_lock_data = lock_file.read()

    input = {
        "file": package_data,
        "lock_file": package_lock_data
    }
    input.update(extract_versions_data)

    with patch.object(PackageExtractor, '_get_versions', side_effect=lambda x: {x: {}}) as mock_get_versions:
        [res], cache = PackageExtractor._extract_versions([input])
        mock_get_versions.assert_called

    assert res == extract_versions_output
    assert cache == {"react": {}, "webpack": {}}


def test_extract_versions_v2():
    with open(os.path.join(test_dir, 'v2', 'package.json'), 'r') as lock_file:
        package_data = lock_file.read()
    with open(os.path.join(test_dir, 'v2', 'package-lock.json'), 'r') as lock_file:
        package_lock_data = lock_file.read()

    input = {
        "file": package_data,
        "lock_file": package_lock_data
    }
    input.update(extract_versions_data)

    with patch.object(PackageExtractor, '_get_versions', side_effect=lambda x: {x: {}}) as mock_get_versions:
        [res], cache = PackageExtractor._extract_versions([input])
        mock_get_versions.assert_called

    assert res == extract_versions_output
    assert cache == {"react": {}, "webpack": {}}


def test_extract_versions_v3():
    with open(os.path.join(test_dir, 'v3', 'package.json'), 'r') as lock_file:
        package_data = lock_file.read()
    with open(os.path.join(test_dir, 'v3', 'package-lock.json'), 'r') as lock_file:
        package_lock_data = lock_file.read()

    input = {
        "file": package_data,
        "lock_file": package_lock_data
    }
    input.update(extract_versions_data)

    with patch.object(PackageExtractor, '_get_versions', side_effect=lambda x: {x: {}}) as mock_get_versions:
        [res], cache = PackageExtractor._extract_versions([input])
        mock_get_versions.assert_called

    output = {}
    output.update(extract_versions_output)
    output.update({
        "package_lock": {}
    })

    assert res == output
    assert cache == {"react": {}, "webpack": {}}


def test_extract_versions_yarn():
    with open(os.path.join(test_dir, 'yarn', 'package.json'), 'r') as lock_file:
        package_data = lock_file.read()
    with open(os.path.join(test_dir, 'yarn', 'yarn.lock'), 'r') as lock_file:
        package_lock_data = lock_file.read()

    input = {
        "file": package_data,
        "lock_file": package_lock_data,
        "lock_variant": "yarn.lock",
    }
    input.update(extract_versions_data)

    with patch.object(PackageExtractor, '_get_versions', side_effect=lambda x: {x: {}}) as mock_get_versions:
        [res], cache = PackageExtractor._extract_versions([input])
        mock_get_versions.assert_called

    output = {}
    output.update(extract_versions_output)
    output.update({
        "lock_variant": "yarn.lock"
    })

    assert res == output
    assert cache == {"react": {}, "webpack": {}}
