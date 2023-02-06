package ru.yandex.autotests.morda.steps;

import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.MordaRequestActions;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URI;
import java.net.URL;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25/05/16
 */
public class UrlSteps {

    public static int getStatusCode(String url) {
        return getStatusCode(url, null);
    }

//    public static int getStatusCode(String url, String userAgent) {
//        if (url.startsWith("//")) {
//            url = "https:" + url;
//        }
//        RestAssuredGetRequest request = new RestAssuredGetRequest(url)
//                .silent();
//        if (userAgent != null) {
//            request.header("User-Agent", userAgent);
//        }
//        return request.readAsResponse().statusCode();
//    }

    public static int getStatusCode(String url, Morda<?> morda) {
        if (url.startsWith("//")) {
            url = "https:" + url;
        }
        RestAssuredGetRequest request = MordaRequestActions.prepareRequest(
                new RestAssuredGetRequest(url).step("ping " + url).silent(),
                morda
        );
        return request.readAsResponse().statusCode();
    }

    private static String getWrongStatusCodeMessage(String url, int statusCode) {
        return url + " - " + statusCode;
    }

    public static Map<String, Integer> getStatusCodes(List<String> urls) {
        return getStatusCodes(urls, null);
    }

    public static Map<String, Integer> getStatusCodes(List<String> urls, Morda<?> morda) {
        Map<String, Integer> statuses = new ConcurrentHashMap<>();
        for (String url : urls) {
            statuses.put(url, getStatusCode(url, morda));
        }
        return statuses;
    }

    public static Map<String, Integer> getStatusCodesInParallel(Collection<String> urls) {
        return getStatusCodesInParallel(urls, null);
    }

    public static Map<String, Integer> getStatusCodesInParallel(Collection<String> urls, Morda<?> morda) {
        Map<String, Integer> statuses = new ConcurrentHashMap<>();
        ExecutorService executor = Executors.newFixedThreadPool(20);

        for (String url : urls) {
            executor.submit(() -> statuses.put(url, getStatusCode(url, morda)));
        }

        executor.shutdown();
        try {
            executor.awaitTermination(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

        return statuses;
    }

    public static void checkResponseCodeSilently(String url, Matcher<Integer> statusMatcher) {
        int statusCode = getStatusCode(url);
        assertThat("Bad response code: \n" + getWrongStatusCodeMessage(url, statusCode), statusCode, statusMatcher);
    }

    @Step("Check response code")
    public static void checkResponseCode(String url, Matcher<Integer> statusMatcher) {
        checkResponseCodeSilently(url, statusMatcher);
    }

    public static void checkResponseCodeSilently(Collection<String> urls, Matcher<Integer> statusMatcher) {
        Map<String, Integer> statuses = getStatusCodesInParallel(urls);
        List<String> errorRequests = statuses.entrySet().stream()
                .filter(s -> !statusMatcher.matches(s.getValue()))
                .map(s -> getWrongStatusCodeMessage(s.getKey(), s.getValue()))
                .collect(Collectors.toList());

        assertThat(StringUtils.join(errorRequests, ", "), errorRequests, hasSize(0));
    }


    @Step("Check response codes")
    public static void checkResponseCode(List<String> urls, Matcher<Integer> statusMatcher) {
        Map<String, Integer> statuses = getStatusCodes(urls);
        List<String> errorRequests = statuses.entrySet().stream()
                .filter(s -> !statusMatcher.matches(s.getValue()))
                .map(s -> getWrongStatusCodeMessage(s.getKey(), s.getValue()))
                .collect(Collectors.toList());

        assertThat("Bad response codes: \n" + StringUtils.join(errorRequests, "\n"), errorRequests, hasSize(0));
    }

    public static void checkResponseCode(URI url, Matcher<Integer> statusMatcher) {
        checkResponseCode(url.toString(), statusMatcher);
    }

    public static void checkResponseCode(URL url, Matcher<Integer> statusMatcher) {
        checkResponseCode(url.toString(), statusMatcher);
    }

    public static void checkResponseCode(String url, int status) {
        checkResponseCode(url, equalTo(status));
    }

    public static void checkResponseCode(URI url, int status) {
        checkResponseCode(url.toString(), status);
    }

    public static void checkResponseCode(URL url, int status) {
        checkResponseCode(url.toString(), status);
    }

}
