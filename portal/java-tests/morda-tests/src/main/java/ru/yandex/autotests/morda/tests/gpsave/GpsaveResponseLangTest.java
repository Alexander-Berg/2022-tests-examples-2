package ru.yandex.autotests.morda.tests.gpsave;

import ch.lambdaj.Lambda;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveRequest;
import ru.yandex.autotests.morda.beans.gpsave.MordaGpSaveResponse;
import ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.morda.matchers.NestedPropertyMatcher;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.beans.GeobaseRegionData;
import ru.yandex.geobase.beans.GeobaseRegionTranslations;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/05/16
 */
@Aqua.Test(title = "GpSave lang")
@RunWith(Parameterized.class)
@Features({"GpSave"})
@Stories({"lang"})
public class GpsaveResponseLangTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected MordaClient mordaClient = new MordaClient();
    protected GeobaseRegion region;
    protected MordaLanguage language;

    public GpsaveResponseLangTest(GeobaseRegion region, MordaLanguage language) {
        this.region = region;
        this.language = language;
    }

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> list = new ArrayList<>();
        for (MordaLanguage language : asList(MordaLanguage.RU, MordaLanguage.UK, MordaLanguage.BE, MordaLanguage.KK)) {
            for (GeobaseRegion region : asList(Russia.MOSCOW, Ukraine.KYIV, Belarus.MINSK, Kazakhstan.ASTANA)) {
                list.add(new Object[]{region, language});
            }
        }
        return list;
    }

    @Test
    public void gpautoTranslation() throws JsonProcessingException {
        GeobaseRegionData regionData = region.getData();
        GeobaseRegionTranslations regionTranslations = region.getTranslations(language.getValue());
        Morda<?> morda = DesktopMainMorda.desktopMain(CONFIG.pages().getEnvironment()).region(region).language(language);
        String sk = mordaClient.cleanvars(morda).read().getSk();
        MordaGpsaveRequest request = mordaClient.gpsave(morda.getUrl(), regionData.getLatitude(), regionData.getLongitude(), 500, sk)
                .withLang(language);

        MordaGpSaveResponse response = request.read();

        checkTranslation(response, AllOfDetailedMatcher.allOfDetailed(
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionName(), Matchers.equalTo(regionTranslations.getNominativeCase())),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionGenitive(), Matchers.equalTo(regionTranslations.getGenitiveCase())),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionLocative(), Matchers.not(Matchers.isEmptyOrNullString())),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionDative(), Matchers.not(Matchers.isEmptyOrNullString())),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getAddress(), Matchers.not(Matchers.isEmptyOrNullString()))
        ));
    }

    @Step("Check translation {1}")
    public void checkTranslation(MordaGpSaveResponse response, Matcher<MordaGpSaveResponse> matcher) {
        assertThat(response, matcher);
    }

}
