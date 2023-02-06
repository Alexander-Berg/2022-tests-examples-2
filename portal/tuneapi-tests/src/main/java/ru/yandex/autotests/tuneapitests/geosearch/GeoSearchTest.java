package ru.yandex.autotests.tuneapitests.geosearch;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.tuneapitests.steps.GeoSearchSteps;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Region;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Search Region")
@RunWith(Parameterized.class)
@Features("Geo Search")
@Stories("Search Region")
public class GeoSearchTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\"; Request: {2}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Region r : Region.values()) {
                data.add(new Object[]{d, r, r.getRegionName()});
                data.add(new Object[]{d, r, r.getRegionName().substring(0, 4).toLowerCase()});
            }
        }
        return data;
    }

    private final Region region;
    private final String request;
    private final GeoSearchSteps userGeoSearch;

    public GeoSearchTest(Domain domain, Region region, String request) {
        this.region = region;
        this.request = request;
        this.userGeoSearch = new GeoSearchSteps(TuneClient.getClient(), domain);
    }

    @Test
    public void geoSearch() throws IOException {
        String resp = userGeoSearch.search(request);
        JsonNode parsedResp = userGeoSearch.shouldSeeCorrectSearchResponse(request, resp);
        userGeoSearch.shouldSeeRegionInResponse(region, parsedResp);
    }
}
