# Приёмочные тесты CMS

## Сценарии
Осуществляют проверку двух базовых сценариев:

### Запрос от Wall-E удовлетворяется успешно
0. Wall-E создаёт запрос на ребут
0. CMS его подтверждает
0. Wall-E удаляет задачу
0. CMS вводит сервер в работу

### Запрос от Wall-E отвергается
0. Wall-E создаёт запрос на ребут
0. CMS его отвергает
0. Wall-E удаляет задачу

## Реализация
Двумя способами:

### Через API
Для простоты тест оформлен как Django-pytest, что бы упростить доступ к frontend API и БД.
Остальные компоненты - через фикстуры.

### Через UI
с использованием Selenium - пока не реализовано.