package ru.yandex.metrika.common.test.medium;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.config.Configurator;

import ru.yandex.metrika.util.log.Log4jSetup;

public class MediumTestsLogSetup {

    public static void setup() {
        // medium-тесты пишут логи в stdout и stderr
        Log4jSetup.basicArcadiaSetup(Level.INFO);

        //Configurator.setLevel(LogManager.getRootLogger().getName(), Level.INFO);
        Configurator.setLevel("ru.yandex.metrika", Level.ALL);
        // Обильное логирование замедляет прохождение тестов, поэтому лишние логи прикрываем
        Configurator.setLevel("ru.yandex.clickhouse", Level.DEBUG);

        Log4jSetup.mute("com.atomikos.jdbc");
        Log4jSetup.mute("ru.yandex.direct.juggler.JugglerAsyncSender");
        Log4jSetup.mute("com.codahale.metrics.graphite.GraphiteReporter");
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
    }
}
