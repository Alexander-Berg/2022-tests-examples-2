package ru.yandex.autotests.morda.steps.links;

import com.jayway.restassured.response.Response;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.HttpResponseInterceptor;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.CookieSpecs;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URI;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.MordaRequestActions.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/16
 */
public class LinkUtils {
    private static final Logger LOGGER = Logger.getLogger(LinkUtils.class);

    public static String normalize(String url) {
        if (url == null || !url.startsWith("//")) {
            return url;
        }
        return "https:" + url;
    }

    public static List<PingResult> ping(Collection<String> urls) {
        return ping(urls, null, null);
    }

    public static List<PingResult> ping(Collection<String> urls, GeobaseRegion region) {
        return ping(urls, region, null);
    }

    public static List<PingResult> ping(Collection<String> urls, MordaLanguage language) {
        return ping(urls, null, language);
    }

    @Step("Ping links")
    public static List<PingResult> ping(Collection<String> urls, Morda<?> morda) {
        Set<String> urlsSet = new HashSet<>(urls);
        urlsSet.remove(null);
        List<PingResult> pingResults = new ArrayList<>();

        PoolingHttpClientConnectionManager cm = new PoolingHttpClientConnectionManager();
        cm.setMaxTotal(200);
        cm.setDefaultMaxPerRoute(20);

        HttpClient httpClient = HttpClients.custom()
                .setConnectionManager(cm)
                .setDefaultRequestConfig(RequestConfig.custom()
                        .setCookieSpec(CookieSpecs.STANDARD).build())
                .addInterceptorFirst((HttpResponseInterceptor) (response, context) -> {
                    Header location = response.getFirstHeader("Location");
                    if (location != null) {
                        String dest = location.getValue();
                        try {
                            URI uri = URI.create(dest);
                            String scheme = uri.getScheme();
                            if (asList("itms-apps", "itms-appss", "itmss").contains(scheme)) {
                                LOGGER.info("Intercept request to '" + uri + "' with status 200");
                                response.setStatusCode(200);
                            }
                        } catch (Exception e) {
                            LOGGER.error(e);
                        }
                    }
                })

                .build();

        ExecutorService executor = Executors.newFixedThreadPool(20);

        for (String url : urlsSet) {
            executor.submit(() -> {
                PingResult res = ping(httpClient, url, morda);
                synchronized (pingResults) {
                    pingResults.add(res);
                }
            });
        }

        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            throw new RuntimeException("Interrupted while pinging links", e);
        }

        AttachmentUtils.attachText("ping_results.info", pingResults.stream()
                .map(PingResult::toString).collect(toList()));

        List<PingResult> failedPings = getFailedRequests(pingResults);
        if (!failedPings.isEmpty()) {
            AttachmentUtils.attachText("failed_pings.info", failedPings.stream()
                    .map(PingResult::toString).collect(toList()));
        }

        return pingResults;
    }

    @Step("Ping links")
    public static List<PingResult> ping(Collection<String> urls, GeobaseRegion region, MordaLanguage language) {
        Set<String> urlsSet = new HashSet<>(urls);
        urlsSet.remove(null);
        List<PingResult> pingResults = new ArrayList<>();

        ExecutorService executor = Executors.newFixedThreadPool(20);

        for (String url : urlsSet) {
            executor.submit(() -> {
                synchronized (pingResults) {
                    PingResult res = ping(url, region, language);
                    pingResults.add(res);
                }
            });
        }

        executor.shutdown();
        try {
            executor.awaitTermination(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            throw new RuntimeException("Interrupted while pinging links", e);
        }

        AttachmentUtils.attachText("ping_results.info", pingResults.stream()
                .map(PingResult::toString).collect(toList()));

        return pingResults;
    }


    public static PingResult ping(String url) {
        return ping(url, null, null);
    }

    public static PingResult ping(String url, GeobaseRegion region) {
        return ping(url, region, null);
    }

    public static PingResult ping(String url, MordaLanguage language) {
        return ping(url, null, language);
    }

    public static PingResult ping(String url, GeobaseRegion region, MordaLanguage language) {
        try {
            url = normalize(url);
            Response response = new RestAssuredGetRequest(url)
                    .beforeRequest(setRegion(region))
                    .beforeRequest(setLanguage(language))
                    .urlEncoding(false)
                    .silent()
                    .readAsResponse();
            return new PingResult(url, response.getStatusCode());
        } catch (Throwable e) {
            return new PingResult(url, e);
        }
    }

    public static PingResult ping(String url, Morda<?> morda) {
        try {
            url = normalize(url);
            Response response = prepareRequest(new RestAssuredGetRequest(url), morda)
                    .silent()
                    .readAsResponse();
            return new PingResult(url, response.getStatusCode());
        } catch (Throwable e) {
            return new PingResult(url, e);
        }
    }

    private static PingResult doPing(HttpClient client, HttpUriRequest request) {
        try {
            HttpResponse response = client.execute(request);
            response.getEntity().getContent().close();
            return new PingResult(request.getURI().toASCIIString(), response.getStatusLine().getStatusCode());
        } catch (Throwable e) {
            return new PingResult(request.getURI().toASCIIString(), e);
        }
    }

    public static PingResult ping(HttpClient client, String url, Morda<?> morda) {
        url = normalize(url);
        HttpGet get = new HttpGet(url);
        get.addHeader("User-Agent", morda.getUserAgent());
        PingResult result = doPing(client, get);

        if (result.isError()) {
            return doPing(client, get);
        }
        return result;
    }

    public static PingResult ping(URI url, Morda<?> morda) {
        return ping(url.toString(), morda);
    }

    public static PingResult ping(URI url) {
        return ping(url.toString());
    }

    public static PingResult ping(URI url, GeobaseRegion region) {
        return ping(url.toString(), region);
    }

    public static PingResult ping(URI url, MordaLanguage language) {
        return ping(url.toString(), language);
    }

    public static PingResult ping(URI url, GeobaseRegion region, MordaLanguage language) {
        return ping(url.toString(), region, language);
    }

    public static List<PingResult> getFailedRequests(List<PingResult> pingResults) {
        return pingResults.stream()
                .filter(e -> e.isError() || e.getStatusCode() != 200)
                .collect(Collectors.toList());
    }

    public static class PingResult {
        private String url;
        private int statusCode;
        private boolean isError;
        private Throwable error;

        public PingResult(String url, int statusCode) {
            this.url = url;
            this.statusCode = statusCode;
            this.isError = false;
        }

        public PingResult(String url, Throwable error) {
            this.url = url;
            this.isError = true;
            this.error = error;
        }

        public Throwable getError() {
            return error;
        }

        public boolean isError() {
            return isError;
        }

        public int getStatusCode() {
            return statusCode;
        }

        public String getUrl() {
            return url;
        }

        @Override
        public String toString() {
            if (isError) {
                return url + "\t>>\t" + error + "\n" + ExceptionUtils.getStackTrace(error);
            }
            return url + "\t>>\t" + getStatusCode();
        }
    }
}
