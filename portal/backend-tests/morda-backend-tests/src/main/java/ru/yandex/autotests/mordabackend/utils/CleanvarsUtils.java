package ru.yandex.autotests.mordabackend.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.net.URI;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
public class CleanvarsUtils {
    @Step("{2}")
    public static <T> void shouldHaveParameter(Object message, T t, Matcher matcher) {
        assertThat(message.toString(), t, matcher);
    }

    @Step("{1}")
    public static <T> void shouldHaveParameter(T t, Matcher matcher) {
        assertThat(t, matcher);
    }

    @Step("{1}")
    public static <T> void shouldMatchTo(String message, T t, Matcher<T> matcher) {
        assertThat(message, t, matcher);
    }

    @Step("{1}")
    public static <T> void shouldMatchTo(T t, Matcher<T> matcher) {
        assertThat(t, matcher);
    }

    public static <T> void shouldMatchTo(T t, Matcher<T>... matchers) {
        for (Matcher<T> m : matchers) {
            shouldMatchTo(t, m);
        }
    }

    @Step("Link \"{1}\" response code {2}")
    public static void shouldHaveResponseCode(Client client, String url, Matcher<Integer> codeMatcher)
            throws IOException {
        int code;
        try {
            code = makeRequest(client, url);
        } catch (Exception e) {
            code = -1;
        }
        try {
            if (code == -1 || !codeMatcher.matches(code)) {
                try {
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
                code = makeRequest(client, url);
            }
            assertThat(normalizeUrl(url), code, codeMatcher);
        } catch (Exception e) {
            fail(e.getMessage());
        }
    }

    private static int makeRequest(Client client, String url) {
        Response response = client
                .target(URI.create(normalizeUrl(url)))
                .request()
                .header("Accept", "*/*")
                .buildGet()
                .invoke();
        int code = response.getStatus();
        response.close();
        return code;
    }

    public static void shouldHaveResponseCode(Client client, String url, UserAgent ua, Matcher<Integer> codeMatcher)
            throws IOException {
        shouldHaveResponseCode("GET " + url, client, url, ua, codeMatcher);
    }

    @Step("Link \"{2}\" response code {4}, {3}")
    public static void shouldHaveResponseCode(String message, Client client, String url, UserAgent ua, Matcher<Integer> codeMatcher)
            throws IOException {
        int code;

        try {
            try {
                code = makeRequest(client, url, ua);
                if (!codeMatcher.matches(code)) {
                    Thread.sleep(5000);
                    code = makeRequest(client, url, ua);
                }
            } catch (Exception e) {
                Thread.sleep(5000);
                code = makeRequest(client, url, ua);
            }
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

        assertThat(message, code, codeMatcher);

    }

    @Attachment(value = "cleanvars.json")
    public static String attach(Object o) {
        return o.toString();
    }

    private static int makeRequest(Client client, String url, UserAgent ua) {
        Response response = client
                .target(URI.create(normalizeUrl(url)))
                .request()
                .header("User-Agent", ua.getValue())
                .header("Accept", "*/*")
                .buildGet()
                .invoke();
        int code = response.getStatus();
        response.close();
        return code;
    }
}
