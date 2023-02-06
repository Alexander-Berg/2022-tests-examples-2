package ru.yandex.metrika.util;

import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.util.concurrent.TimeoutExecutorService;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertTrue;

/**
 * @author jkee
 */

public class TimeoutExecutorServiceTest {

    private static final Logger log = LoggerFactory.getLogger(TimeoutExecutorServiceTest.class);
    TimeoutExecutorService service;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup();
        service = new TimeoutExecutorService(5500);
    }

    @Test
    public void testSubmit() throws Exception {
        Runnable task = new Runnable() {
            @Override
            public void run() {
                for (int i = 0; i < 10; i++) {
                    try {
                        Thread.sleep(1000);
                        log.info("{} interations passed", i);
                    } catch (InterruptedException e) {
                        log.info("Interrupted");
                        return;
                    }
                }
            }
        };
        long time = System.currentTimeMillis();
        service.submit(task);
        assertTrue(System.currentTimeMillis() - time < 6000);
        Thread.sleep(5000);
    }
}
