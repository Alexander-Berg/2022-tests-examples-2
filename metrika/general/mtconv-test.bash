#!/bin/bash

bash -c 'echo audience-intapid-test.metrika.yandex.{ru,net}
echo mobmet-intapid-test.metrika.yandex.ru
echo internalapi-test.metrika.yandex.{ru,net}
echo mtconv01t.haze.yandex.net
echo mtconv01gt.yandex.ru' | tr '\n' ',' | tr ' ' ',' ; echo
