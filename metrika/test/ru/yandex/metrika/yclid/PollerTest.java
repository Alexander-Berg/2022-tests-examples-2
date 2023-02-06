package ru.yandex.metrika.yclid;

import java.util.concurrent.CompletableFuture;

import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
@Ignore
public class PollerTest {

    private Poller poller;

    @Before
    public void setUp() throws Exception {
        poller = new Poller();
    }

    @Test
    public void testSubmitUrl() throws Exception {
        CompletableFuture<CheckResult> f = poller.submitUrl2("http://yandex.ru", x -> System.out.println(x.html));
        f.join();
    }

    @After
    public void tearDown() throws Exception {
        poller.shutdown();
    }
}
