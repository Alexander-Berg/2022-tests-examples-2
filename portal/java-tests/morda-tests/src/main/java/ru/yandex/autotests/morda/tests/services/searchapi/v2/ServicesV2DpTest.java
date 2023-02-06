package ru.yandex.autotests.morda.tests.services.searchapi.v2;

import ar.com.hjg.pngj.ImageInfo;
import ar.com.hjg.pngj.PngReader;
import org.hamcrest.Matcher;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Entry;
import ru.yandex.autotests.morda.data.services.searchapi.ServicesSearchApiV2Data;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.Tag;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._1;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._2;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._3;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._4;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "DP SearchApi-v2 Services")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.SERVICES})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class ServicesV2DpTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private String service;

    public ServicesV2DpTest(String service) {
        this.service = service;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<String> data() {
        Set<String> services = new HashSet<>();
        for (MordaDomain d : asList(MordaDomain.RU, MordaDomain.UA, MordaDomain.KZ, MordaDomain.BY)) {
            services.addAll(
                    ServicesSearchApiV2Data.getAvailableServices(d)
                            .stream()
                            .map(ServicesV122Entry::getId)
                            .collect(Collectors.toSet()));
        }
        services.add("more");
//        services.add("browser_api");
        return services;
    }

    @Test
    public void dp() {
        String urlPattern = "https://api.yastatic.net/morda-logo/i/yandex-app/informer/services/" + service + ".%s.png";

        PngReader png = new PngReader(new RestAssuredGetRequest(String.format(urlPattern, _1))
                .readAsResponse().asInputStream());
        ImageInfo imageInfo1 = png.imgInfo;
        png.end();

        for (SearchApiDp dp : asList(_2, _3, _4)) {
            int expW = (int) Math.round(imageInfo1.rows * dp.getMult());
            int expH = (int) Math.round(imageInfo1.cols * dp.getMult());
            checkPng(dp, String.format(urlPattern, dp.getValue()), expW, expH);
        }
    }

    @Step("Check size dp={0}, expW={2}, expH={3} ")
    public void checkPng(SearchApiDp dp, String url, int expW, int expH) {
        PngReader png = new PngReader(new RestAssuredGetRequest(url).readAsResponse().asInputStream());
        ImageInfo imageInfo = png.imgInfo;
        png.end();

        if ("browser_api".equals(service)) {
            int delta = expW % 40;
            assertThat(imageInfo.rows, between(expW - delta, expW));
            assertThat(imageInfo.cols, between(expH - delta, expH));
        } else {
            assertThat(imageInfo.rows, equalTo(expW));
            assertThat(imageInfo.cols, equalTo(expH));
        }

    }

    private Matcher<Integer> between(int min, int max) {
        return allOf(greaterThanOrEqualTo(min), lessThanOrEqualTo(max));
    }

}
