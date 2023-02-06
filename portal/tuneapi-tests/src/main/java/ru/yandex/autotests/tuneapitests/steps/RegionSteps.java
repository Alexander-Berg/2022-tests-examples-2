package ru.yandex.autotests.tuneapitests.steps;

import org.apache.http.cookie.Cookie;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientProperties;
import org.hamcrest.Matcher;
import ru.yandex.autotests.cookiemy.CookieMyParser;
import ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory;
import ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils;
import ru.yandex.autotests.morda.utils.cookie.parsers.y.YCookieParser;
import ru.yandex.autotests.morda.utils.cookie.parsers.y.YpCookieValue;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Region;
import ru.yandex.autotests.tuneapitests.utils.SynCookieUtils;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.RedirectionException;
import javax.ws.rs.client.Client;
import javax.ws.rs.core.Configurable;
import javax.ws.rs.core.Response;

import java.lang.reflect.Method;
import java.net.URI;
import java.util.List;
import java.util.Map;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.Assert.fail;

/**
 * User: leonsabr
 * Date: 14.06.12
 */
public class RegionSteps {
    private final Client client;
    private final Domain domain;
    private final MordaCookieUtils<Cookie> cookieUtils;

    public RegionSteps(Client client, Domain domain) {
        this.client = client;
        this.domain = domain;
        this.cookieUtils = CookieUtilsFactory.cookieUtils(client);
    }

    @Step("Set region {0} with retpath {1}")
    public void setRegion(Region region, String retpath) {
        setRegion(domain, region.getRegionId(), null, cookieUtils.getSecretKey(domain.getCookieDomain()), retpath).close();
    }

    @Step("Set region {0} with retpath {1}")
    public void setRegionByName(Region region, String retpath) {
        setRegion(domain, null, region.getRegionName(), cookieUtils.getSecretKey(domain.getCookieDomain()), retpath).close();
    }

    @Step("Set region {0} with wrong sk \"{1}\" and retpath {2}")
    public void setRegionWithWrongSk(Region region, String sk, String retpath) {
        setRegion(domain, region.getRegionId(), null, sk, retpath).close();
    }

    @Step("Set no_location {0} with retpath {1}")
    public void setNoLocation(String noLocation, String retpath) {
        regionActions(domain, null, cookieUtils.getSecretKey(domain.getCookieDomain()), retpath, noLocation, null, null).close();
    }

    @Step("Should see no_location {0} in yp in ygd")
    public void shoulSeeNoLocationInYp(String noLocation) {
        String yp = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yp", domain.getCookieDomain()));
        assertThat(yp, notNullValue());
        Map<String, YpCookieValue> ypCookie = YCookieParser.parseYpCookieToMap(yp);
        assertThat("No subcookie ygd", ypCookie.containsKey("ygd"), equalTo(true));
        assertThat(ypCookie.get("ygd").getValue(), equalTo(noLocation));
    }

    @Step("Should not see no_location in yp in ygd")
    public void shoulNotSeeNoLocationInYp() {
        String yp = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yp", domain.getCookieDomain()));
        if (yp != null) {
            Map<String, YpCookieValue> ypCookie = YCookieParser.parseYpCookieToMap(yp);
            if (ypCookie.containsKey("ygd")) {
                assertThat(ypCookie.get("ygd").getValue(), equalTo("0"));
            }
        }
    }

    @Step("Set region {0} with from {1} with retpath {2}")
    public void setRegionWithFrom(Region region, Region from, String retpath) {
        regionActions(domain, region.getRegionId(),
                cookieUtils.getSecretKey(domain.getCookieDomain()), retpath, null, null, from.getRegionId()).close();
    }

    @Step("Should see {1}:{0} in yp in ygo")
    public void shoulSeeYgoInYp(String regionId, String from) {
        String yp = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yp", domain.getCookieDomain()));
        assertThat(yp, notNullValue());
        Map<String, YpCookieValue> ypCookie = YCookieParser.parseYpCookieToMap(yp);
        assertThat("No subcookie ygo", ypCookie.containsKey("ygo"), equalTo(true));
        assertThat(ypCookie.get("ygo").getValue(), equalTo(from + "%3A" + regionId));
    }

    @Step("Set auto {0} with retpath {1}")
    public void setAuto(String auto, String retpath) {
        regionActions(domain, null, cookieUtils.getSecretKey(domain.getCookieDomain()), retpath, null, auto, null).close();
    }

    public void shouldSeeRegionId(String regionId) {
        shouldSeeRegionId(equalTo(regionId));
    }

    @Step("Should see region id {0}")
    public void shouldSeeRegionId(Matcher<String> regionId) {
        String actualRegionId = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yandex_gid", domain.getCookieDomain()));
        assertThat(actualRegionId, regionId);
    }

    @Step("Should see region id {0} with my 43={2}")
    public void shouldSeeRegionIdWithMy(String regionId, List<String> regionHistory) {
        String actualRegionId = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yandex_gid", domain.getCookieDomain()));
        assertThat(actualRegionId, equalTo(regionId));

        String actualMy = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("my", domain.getCookieDomain()));
        assertThat(actualMy, notNullValue());
        assertThat(CookieMyParser.parse(actualMy).get("43"), equalTo(regionHistory));
    }

    @Step("Should see that region not set")
    public void shouldNotSeeRegionSet() {
        String actualRegionId = cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yandex_gid", domain.getCookieDomain()));
        assertThat(actualRegionId, nullValue());
    }

    @Step("Set region {0} with json response")
    public TuneResponse setRegionJson(Region region, String json) {
        return setRegionJson(domain.getTuneUrl(), region.getRegionId(), cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set region {0} on tune-internal with json response")
    public TuneResponse setRegionJsonOnTuneInternal(Region region, String json) {
        return setRegionJson(domain.getTuneInternalUrl(), region.getRegionId(), cookieUtils.getSecretKey(domain.getCookieDomain()), json);
    }

    @Step("Set region {0} with json response without sk")
    public TuneResponse setRegionJsonWithoutSk(Region region, String json) {
        return setRegionJson(domain.getTuneUrl(), region.getRegionId(), null, json);
    }

    public String getActualRegionId() {
        return cookieUtils.getCookieValue(cookieUtils.getCookieNamed("yandex_gid", domain.getCookieDomain()));
    }

    public Response setRegion(Domain domain, String regionId, String name, String sk, String retpath) {
        Response r = new TuneClient(domain.getTuneUrlForGeoApi())
                .region()
                .withRegionId(regionId)
                .withName(name)
                .withSk(sk)
                .withRetpath(retpath)
                .build()
                .get(client);
        SynCookieUtils.synKUBRCookies(client, "my", "yandex_gid", "yp");
        return r;
    }

    public TuneResponse setRegionJson(URI tuneUri, String region, String sk, String json) {
        client.property(ClientProperties.FOLLOW_REDIRECTS, false);
        TuneResponse response = null;
        try {
            response = new TuneClient(tuneUri)
                    .region()
                    .withRegionId(region)
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

    public Response regionActions(Domain domain, String regionId, String sk, String retpath, String noLocation, String auto, String from) {
        Response r = new TuneClient(domain.getTuneUrlForGeoApi())
                .region()
                .withRegionId(regionId)
                .withNoLocation(noLocation)
                .withAuto(auto)
                .withFrom(from)
                .withSk(sk)
                .withRetpath(retpath)
                .build()
                .get(client);
        SynCookieUtils.synKUBRCookies(client, "my", "yandex_gid", "yp");
        return r;
    }
}