# Лунапарк
## Что это
Лунапарк - яндексовый фреймворк для поддержки нагрузочного тестирования. Позволяет через веб интерфейс запускать стрельбы (нагрузочное тестирование) с Яндекс.Танка и Dolbilo.

## Общее
Основная документация [на вики](https://wiki.yandex-team.ru/load/). Предоставляет [веб интерфейс](https://lunapark.yandex-team.ru/), через который, в частности, можно [запустить стрельбу](https://lunapark.yandex-team.ru/firestarter/) с одного из публичных или со своего танка, посмотреть текущие и прошедшие стрельбы, их статус и статистику (разные полезные графики).

## Танки морды
У морды есть свои танки, которые предпочтительно использовать вместо публичных (т.к. всегда доступны (ибо редко используются) и можно занимать надолго).
Живут в няне в директории `/portal/morda/tank/`, раздельные для каждого ДЦ (т.к. стрелять кросс-ДЦ смысла мало). Выделены для датацентров в [MAN](https://nanny.yandex-team.ru/ui/#/services/catalog/morda_tank_man/), [SAS](https://nanny.yandex-team.ru/ui/#/services/catalog/morda_tank_sas/) и [VLA](https://nanny.yandex-team.ru/ui/#/services/catalog/morda_tank_vla/).

## Как и для чего использовать
Для того, чтобы нагрузить бэкенд или весь граф (аппхостовый) для проверки того, что сервис выдерживает нагрузку и не деградирует со временем.
В частности, можно использовать [Пандору](./pandora.md) для обстрела по GRPC, в частности, обстрела аппхостовых бэкендов (отдельных вершин, без запуска всего графа).