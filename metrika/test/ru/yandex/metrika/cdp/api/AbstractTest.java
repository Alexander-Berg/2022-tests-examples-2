package ru.yandex.metrika.cdp.api;

import org.apache.logging.log4j.Level;
import org.junit.BeforeClass;

import ru.yandex.metrika.util.log.Log4jSetup;

public abstract class AbstractTest {

    @BeforeClass
    public static void beforeClass() {
        Log4jSetup.basicArcadiaSetup(Level.DEBUG);
    }
}
