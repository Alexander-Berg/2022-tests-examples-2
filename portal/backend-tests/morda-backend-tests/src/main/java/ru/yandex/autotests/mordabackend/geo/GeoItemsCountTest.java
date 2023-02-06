package ru.yandex.autotests.mordabackend.geo;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geo.GeoItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEO;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TRAFFIC;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.YYYYMMDD;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.GEO_REGIONS_MAIN;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.getExpectedIcons;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.getExpectedLinks;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: ivannik
 * Date: 21.07.2014
 */
@Aqua.Test(title = "Geo Items Count")
@Features("Geo")
@Stories("Geo Items Count")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoItemsCountTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(YYYYMMDD, TRAFFIC, GEO);

    private Region region;
    private Language language;
    private Cleanvars cleanvars;

    public GeoItemsCountTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                             Region region, Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.cleanvars = cleanvars;
    }

    @Test
    public void iconsCount() {
        List<String> icons = extract(cleanvars.getGeo().getListIcon(), on(GeoItem.class).getService());
        List<String> expectedIcons = getExpectedIcons(region, language, cleanvars);

        assertThat("Actual: " + icons, icons, hasSameItemsAsList(expectedIcons));
    }

    @Test
    public void linksCount() {
        List<String> links = extract(cleanvars.getGeo().getList(), on(GeoItem.class).getService());
        List<String> expectedLinks = getExpectedLinks(region, language, cleanvars);

        assertThat("Actual: " + links, links, hasSameItemsAsList(expectedLinks));
    }
}
