npm run build &&
rm -rf ./e2e/results &&
touch ./e2e/test.log &&
touch ./e2e/prev.test.log &&
cat ./e2e/test.log > ./e2e/prev.test.log &&
node --nolazy ./dist/cli.js --noCheckout --context ./e2e -c types.backend-cpp.config.json > ./e2e/test.log &&
node --nolazy ./dist/cli.js --noCheckout --context ./e2e >> ./e2e/test.log &&
node --nolazy ./dist/cli.js --noCheckout --context ./e2e -c types.scoped.config.json --scope "schemas backend-py3-partial:clownductor uservices-arc:partial" >> ./e2e/test.log &&
./node_modules/.bin/tsc -p ./e2e/tsconfig.json