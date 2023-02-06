package ru.yandex.autotests.morda.tests.gpsave;

import ch.lambdaj.Lambda;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.gpsave.MordaGpSaveResponse;
import ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.morda.matchers.NestedPropertyMatcher;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.Language;
import ru.yandex.geobase.beans.GeobaseRegionData;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/05/16
 */
@Aqua.Test(title = "GpSave flags")
@RunWith(Parameterized.class)
@Features({"GpSave"})
@Stories({"flags"})
public class GpsaveFlagsTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected MordaClient mordaClient = new MordaClient();
    protected Morda<?> morda;
    protected GeobaseRegion region1;
    protected GeobaseRegion region2;
    protected String ip1;
    protected String ip2;
    protected String sk;

    public GpsaveFlagsTest(GeobaseRegion region1, String ip1, GeobaseRegion region2, String ip2) {
        this.region1 = region1;
        this.region2 = region2;
        this.ip1 = ip1;
        this.ip2 = ip2;
    }

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> data() {
        List<Object[]> list = new ArrayList<>();

        list.add(new Object[]{Russia.MOSCOW, "89.175.217.44", Russia.SAINT_PETERSBURG, "31.193.122.100"});
        list.add(new Object[]{Ukraine.KYIV, "46.173.146.76", Ukraine.KHARKIV, "109.87.126.248"});
        list.add(new Object[]{Belarus.MINSK, "93.84.10.197", Belarus.VITEBSK, "37.45.82.133"});
        list.add(new Object[]{Kazakhstan.ASTANA, "2.75.212.68", Kazakhstan.ALMATY, "195.82.12.155"});

        return list;
    }

    @Before
    public void setUp() {
        morda = desktopMain(CONFIG.pages().getEnvironment()).region(region1);
        sk = mordaClient
                .cleanvars(morda.getUrl())
                .header("X-Forwarded-For", ip1)
                .read()
                .getSk();
    }

    @Test
    public void shouldReloadWithDifferentCoords() throws JsonProcessingException {
        GeobaseRegionData regionData1 = region1.getData();
        GeobaseRegionData regionData2 = region2.getData();

        mordaClient.gpsave(morda.getUrl(), regionData1.getLatitude(), regionData1.getLongitude(), 500, sk)
                .header("X-Forwarded-For", ip1)
                .read();

        MordaGpSaveResponse response = mordaClient.gpsave(morda.getUrl(), regionData2.getLatitude(), regionData2.getLongitude(), 500, sk)
                .header("X-Forwarded-For", ip2)
                .read();

        assertThat(response, AllOfDetailedMatcher.allOfDetailed(
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).isShouldReload(), Matchers.is(true)),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).isRegionChanged(), Matchers.is(true)),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionName(), Matchers.equalTo(region2.getTranslations(Language.RU).getNominativeCase()))
        ));
    }

    @Test
    public void shouldNotReloadWithSameIp() throws JsonProcessingException {
        GeobaseRegionData regionData1 = region1.getData();

        MordaGpSaveResponse response = mordaClient.gpsave(morda.getUrl(), regionData1.getLatitude(), regionData1.getLongitude(), 500, sk)
                .header("X-Forwarded-For", ip1)
                .read();

        assertThat(response, AllOfDetailedMatcher.allOfDetailed(
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).isShouldReload(), Matchers.is(false)),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).isRegionChanged(), Matchers.is(false)),
                NestedPropertyMatcher.hasPropertyWithValue(Lambda.on(MordaGpSaveResponse.class).getRegionName(), Matchers.equalTo(region1.getTranslations(Language.RU).getNominativeCase()))
        ));
    }

}
