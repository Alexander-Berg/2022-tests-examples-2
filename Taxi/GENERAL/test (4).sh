#!/bin/bash

../../node_modules/.bin/tslint --test ./test/ban-binded-common-action-in-saga-rule/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/grouped-imports/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/prefer-extended-props/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/single-saga-per-component/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/cross-bundle-imports/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/no-default-lodash-import/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/typed-yield/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/typed-yield/strict/tslint.json &&
../../node_modules/.bin/tslint --test ./test/restricted-imports/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/cross-layers-imports/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/routing-import-restriction/default/tslint.json &&
../../node_modules/.bin/tslint --test ./test/disallowed-substring/default/tslint.json
