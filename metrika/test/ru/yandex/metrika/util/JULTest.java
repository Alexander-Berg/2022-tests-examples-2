package ru.yandex.metrika.util;

import java.util.logging.Logger;

import org.junit.Test;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;

import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * jul to slf4j test
 * @author lemmsh
 * @since 4/25/14
 */

public class JULTest {

    @Test
    public void testLog() throws Exception {

        Log4jSetup.basicSetup();
        org.slf4j.Logger slfLog = LoggerFactory.getLogger("slf");
        Logger log = Logger.getLogger("jul");
        log.info("jul log");
        slfLog.info("slf log");
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();

        log.info("jul log after bridge");
    }
}
