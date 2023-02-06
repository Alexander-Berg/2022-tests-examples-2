package ru.yandex.metrika.metr19972;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@Ignore
public class GAQuotaTest {

    private static final String OAUTH_TOKEN = "fake_token";

    @Test
    public void sendRequestAndChecksQuota() throws Exception {
        TimeUnit.SECONDS.sleep(1);

        final CountDownLatch latch = new CountDownLatch(1);

        ExecutorService executorService = Executors.newFixedThreadPool(100);
        List<Future> res = new ArrayList<>();
        Runnable r = () -> {
            try {
                CloseableHttpClient client = HttpClients.createDefault();
                HttpGet httpGet = new HttpGet("http://localhost:8082/analytics/v3/data/ga?" +
                        "oauth_token=" + OAUTH_TOKEN + "&" +
                        "ids=ga:23441518&" +
                        "dimensions=ga:date&" +
                        "metrics=ga:sessions,ga:users&" +
                        "start-date=2016-01-01&" +
                        "end-date=2016-01-31&" +
                        "max-results=10000&" +
                        "start-index=1&" +
                        "filters=ga:medium==organic;ga:source==yandex.ru;ga:keyword=~%28%28энергосбереж%7Cстроит%29.%2A%3F%29%7B2%7D;ga:keyword!~промышлен;ga:keyword!~производствен;ga:keyword!~программ;ga:keyword!~обеспечен;ga:keyword!~проект;ga:keyword!~ackye.ru"
                );
                latch.await();
                long startTime = System.currentTimeMillis();
                CloseableHttpResponse response = client.execute(httpGet);
                long endTime = System.currentTimeMillis();
                String respContent = IOUtils.toString(response.getEntity().getContent());
                Date startDateTime = new Date(startTime);
                Date endDateTime = new Date(endTime);
                System.out.println(
                        response.getStatusLine().getStatusCode() +
                                " [" + startDateTime.toString() + ':' + endDateTime.toString() + ']' +
                                Thread.currentThread().getName() + ' ' +
                                respContent);
                assertTrue(respContent.startsWith("{\"kind\":\"analytics#gaData\""));
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
        for (int i = 0; i < 100; i++) {
            res.add(executorService.submit(r));
        }
        TimeUnit.SECONDS.sleep(1);
        latch.countDown();
        executorService.awaitTermination(1000, TimeUnit.MILLISECONDS);
        assertEquals(0, res.stream().filter(f -> {
            try {
                return (f.get() instanceof AssertionError);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }).count());
    }

}
