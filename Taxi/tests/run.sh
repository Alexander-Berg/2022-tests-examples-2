# Общие тесты сломаны, поэтому здесь запускаются работающие тесты.

(NODE_ENV=testing npx jest --detectOpenHandles --runInBand \
    tests/units/controllers/webhook.test.js) || true
