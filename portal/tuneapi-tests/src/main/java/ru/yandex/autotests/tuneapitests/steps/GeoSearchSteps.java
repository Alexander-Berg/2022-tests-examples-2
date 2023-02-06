package ru.yandex.autotests.tuneapitests.steps;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.cookie.Cookie;
import ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory;
import ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Region;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.io.IOException;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.fail;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GeoSearchSteps {
    private final Client client;
    private final Domain domain;
    private final MordaCookieUtils<Cookie> cookieUtils;

    public GeoSearchSteps(Client client, Domain domain) {
        this.client = client;
        this.domain = domain;
        this.cookieUtils = CookieUtilsFactory.cookieUtils(client);
    }

    @Step("Search {0}")
    public String search(String request) {
        return search(domain, request).readEntity(String.class);
    }

    @Step("Should see correct search response")
    public JsonNode shouldSeeCorrectSearchResponse(String request, String resp) {
        JsonNode jn;
        try {
            jn = new ObjectMapper().readTree(resp);
        } catch (IOException e) {
            throw new AssertionError("Search response incorrect", e);
        }
        assertThat(jn.get(0).textValue(), equalTo(request));
        assertThat(jn.get(2).toString(), equalTo("{\"r\":1}"));
        return jn;
    }

    @Step("Should see region id {0} in search response")
    public void shouldSeeRegionInResponse(Region region, JsonNode resp) {
        for (JsonNode respItem : resp.get(1)) {
            if (respItem.get(1).toString().equals(region.getRegionId())) {
                return;
            }
        }
        fail("Region " + region + " not found in response");
    }

    public Response search(Domain domain, String request) {
        return new TuneClient(domain.getTuneUrl())
                .geoSearch()
                .withPart(request)
                .build()
                .get(client);
    }
}
