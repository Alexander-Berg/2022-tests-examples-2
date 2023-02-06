package ru.yandex.autotests.tuneapitests.steps;

import org.apache.http.cookie.Cookie;
import org.glassfish.jersey.client.ClientProperties;
import ru.yandex.autotests.cookiemy.CookieMyParser;
import ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory;
import ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Language;
import ru.yandex.autotests.tuneapitests.utils.SynCookieUtils;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.RedirectionException;
import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.net.URI;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static org.junit.Assert.fail;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class LanguageSteps {
    private final Client client;
    private final Domain domain;
    private final MordaCookieUtils<Cookie> cookieUtils;

    public LanguageSteps(Client client, Domain domain) {
        this.client = client;
        this.domain = domain;
        this.cookieUtils = CookieUtilsFactory.cookieUtils(client);
    }

    @Step("Set language {0} with retpath {1}")
    public void setLanguage(String intl, String retpath) {
        setLanguage(domain, intl, cookieUtils.getSecretKey(domain.getCookieDomain()), retpath).close();
    }

    @Step("Set language {0} with wrong sk \"{1}\" and retpath {2}")
    public void setLanguageWithWrongSk(String intl, String sk, String retpath) {
        setLanguage(domain, intl, sk, retpath).close();
    }

    @Step("Should see language {0}")
    public void shouldSeeLanguage(Language lang) {
        String actualMy = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("my", domain.getCookieDomain()));
        assertThat(actualMy, notNullValue());
        List<String> parsedIntl = CookieMyParser.parse(actualMy).get("39");
        assertThat(parsedIntl.get(1), equalTo(lang.getMyValue()));
    }

    @Step("Should see that language not set")
    public void shouldNotSeeLanguageSet() {
        String actualMy = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("my", domain.getCookieDomain()));
        if (actualMy != null) {
            assertThat(CookieMyParser.parse(actualMy).get("39"), nullValue());
        }
    }

    @Step("Set language {0} with json response")
    public TuneResponse setLanguageJson(String intl, String json) {
        return setLanguageJson(domain.getTuneUrl(), intl, cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set language {0} on tune-internal with json response")
    public TuneResponse setLanguageJsonOnTuneInternal(String intl, String json) {
        return setLanguageJson(domain.getTuneInternalUrl(), intl, cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set language {0} with json response without sk")
    public TuneResponse setLanguageJsonWithoutSk(String intl, String json) {
        return setLanguageJson(domain.getTuneUrl(), intl, null, json);
    }

    private Response setLanguage(Domain domain, String intl, String sk, String retpath) {
        Response r = new TuneClient(domain.getTuneUrl()).language()
                .withIntl(intl)
                .withSk(sk)
                .withRetpath(retpath)
                .build()
                .get(client);
        SynCookieUtils.synKUBRCookies(client, "my", "yandex_gid", "yp");
        return r;
    }

    public TuneResponse setLanguageJson(URI tuneUri, String intl, String sk, String json) {
        client.property(ClientProperties.FOLLOW_REDIRECTS, false);
        TuneResponse response = null;
        try {
            response = new TuneClient(tuneUri)
                    .language()
                    .withIntl(intl)
                    .withSk(sk)
                    .withJson(json)
                    .build()
                    .getTuneResponse(client);
        } catch (RedirectionException e) {
            fail("Found redirect when requesting json: " + e.getLocation());
        } finally {
            client.property(ClientProperties.FOLLOW_REDIRECTS, true);
        }
        return response;
    }
}
