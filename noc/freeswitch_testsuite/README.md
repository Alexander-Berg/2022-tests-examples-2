Testsuite запускается командой run_tests
Обязательный параметр --path указывает на путь к бинарнику freeswitch

# Базовые тесты:
Тесты входящих звонков:
- Входящий, dispatcher отвечает ошибкой > 400
- Входящий, dispatcher возвращает неизвестную команду
- Входящий, dispatcher отбивает со специфичным кодом
- Входящий, dispatcher отвечает и сразу завершает звонок
- Входящий, ответ, playback, hangup со стороны dispatcher
- Входящий, ответ, speak, hangup со стороны dispatcher
- Входящий, ответ, ask с промптом, hangup со стороны dispatcher
- Входящий, ответ, ask с синтезом, hangup со стороны dispatcher
- Входящий, ответ, playback, hangup со стороны UAC

Тесты исходящих звонков:
- Исходящий, не можем распарсить JSON в create_leg
- Входящий, dispatcher возвращает initial без нужного параметра
- Исходящий, dispatcher отвечает ошибкой > 400 в ответ на initial, заказываем session_id
- Исходящий, dispatcher отвечает ошибкой > 400 в ответ на initial, произвольный session_id
- Исходящий, dispatcher возвращает неизвестную команду в ответ на initial
- Исходящий до sip-клиента, недоступен UAS
- Исходящий до sip-клиента, UAS отбивает со специфичным кодом
- Исходящий до sip-клиента, UAS не отвечает
- Исходящий до sip-клиента, ответ, playback, hangup со стороны dispatcher

# Тесты команд:
TBD
