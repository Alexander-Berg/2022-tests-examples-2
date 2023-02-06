package ru.yandex.autotests.tuneapitests.steps;

import org.apache.http.cookie.Cookie;
import org.glassfish.jersey.client.ClientProperties;
import ru.yandex.autotests.cookiemy.CookieMyParser;
import ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory;
import ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils;
import ru.yandex.autotests.tuneapitests.utils.Domain;
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
public class MyCookieSteps {
    private final Client client;
    private final Domain domain;
    private final MordaCookieUtils<Cookie> cookieUtils;

    public MyCookieSteps(Client client, Domain domain) {
        this.client = client;
        this.domain = domain;
        this.cookieUtils = CookieUtilsFactory.cookieUtils(client);
    }

    @Step("Set in my {0}={1} with retpath {2}")
    public void setMy(String block, List<String> params, String retpath) {
        setMy(domain, block, params, cookieUtils.getSecretKey(domain.getCookieDomain()), retpath).close();
    }

    @Step("Set in my {0}={1} with wrong sk \"{2}\" and retpath {3}")
    public void setMyWithWrongSk(String block, List<String> params, String sk, String retpath) {
        setMy(domain, block, params, sk, retpath).close();
    }

    @Step("Should see my cookie {0}={1}")
    public void shouldSeeMyCookie(String block, List<String> params) {
        String actualMy = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("my", domain.getCookieDomain()));
        assertThat(actualMy, notNullValue());
        List<String> parsedMyBlock = CookieMyParser.parse(actualMy).get(block);
        assertThat(parsedMyBlock, equalTo(params));
    }

    @Step("Should see that my cookie param in {0} not set")
    public void shouldNotSeeMyCookieParamSet(String block) {
        String actualMy = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("my", domain.getCookieDomain()));
        if (actualMy != null) {
            List<String> parsedMyBlock = CookieMyParser.parse(actualMy).get(block);
            assertThat(parsedMyBlock, nullValue());
        }
    }

    @Step("Set in my {0}={1} with json response")
    public TuneResponse setMyJson(String block, List<String> params, String json) {
        return setMyJson(domain.getTuneUrl(), block, params, cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set in my {0}={1} on tune-internal with json response")
    public TuneResponse setMyJsonOnTuneInternal(String block, List<String> params, String json) {
        return setMyJson(domain.getTuneInternalUrl(), block, params, cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set in my {0}={1} with json response without sk")
    public TuneResponse setMyJsonWithoutSk(String block, List<String> params, String json) {
        return setMyJson(domain.getTuneUrl(), block, params, null, json);
    }

    public Response setMy(Domain domain, String block, List<String> params, String sk, String retpath) {
        Response r = new TuneClient(domain.getTuneUrl())
                .my()
                .withBlock(block)
                .withParams(params)
                .withSk(sk)
                .withRetpath(retpath)
                .build()
                .get(client);
        SynCookieUtils.synKUBRCookies(client, "my", "yandex_gid", "yp");
        return r;
    }

    public TuneResponse setMyJson(URI tuneUri, String block, List<String> params, String sk, String json) {
        client.property(ClientProperties.FOLLOW_REDIRECTS, false);
        TuneResponse response = null;
        try {
            response = new TuneClient(tuneUri)
                    .my()
                    .withBlock(block)
                    .withParams(params)
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
