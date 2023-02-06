package ru.yandex.autotests.morda.tests.gpsave;

import com.jayway.restassured.response.Response;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveDevice;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveFormat;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveRequest;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.beans.GeobaseRegionData;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.cookies.y.CookieYp;
import ru.yandex.qatools.cookies.y.blocks.GpautoBlock;
import ru.yandex.qatools.cookies.y.matchers.GpautoMatcher;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/05/16
 */
@Aqua.Test(title = "GpSave yp_gpauto_value")
@RunWith(Parameterized.class)
@Features({"GpSave"})
@Stories({"yp_gpauto_value"})
public class GpsaveCookieTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected GeobaseRegion region;
    protected MordaLanguage language;
    protected MordaGpsaveDevice device;
    protected MordaGpsaveFormat format;
    protected int precision;
    protected MordaGpsaveRequest request;

    public GpsaveCookieTest(GeobaseRegion region, MordaLanguage language, MordaGpsaveDevice device, MordaGpsaveFormat format, int precision) {
        this.region = region;
        this.language = language;
        this.device = device;
        this.format = format;
        this.precision = precision;
    }

    @Parameterized.Parameters(name = "{0}, {1}, {2}, {3}, {4}")
    public static Collection<Object[]> data() {
        List<Object[]> list = new ArrayList<>();
        for (MordaLanguage language : asList(MordaLanguage.RU, MordaLanguage.UK, MordaLanguage.BE, MordaLanguage.KK)) {
            for (GeobaseRegion region : asList(Russia.MOSCOW, Ukraine.KYIV, Belarus.MINSK, Kazakhstan.ASTANA)) {
                for (MordaGpsaveDevice device : MordaGpsaveDevice.values()) {
                    for (MordaGpsaveFormat format : MordaGpsaveFormat.values()) {
                        list.add(new Object[]{region, language, device, format, 500});
                    }
                }
            }
        }
        return list;
    }

    @Before
    public void createRequest() {
        MordaWithRegion morda = DesktopMainMorda.desktopMain(CONFIG.pages().getEnvironment()).region(region).language(language);
        MordaClient mordaClient = new MordaClient();
        this.request = mordaClient.gpsave(morda, precision, device, format);
    }

    @Test
    public void gpautoCookieIsSet() {
        GeobaseRegionData regionData = region.getData();
        Response response = request.readAsResponse();
        GpautoBlock gpautoBlock = new CookieYp(response.cookie("yp")).gpauto();
        assertThat("Block gpauto not found", gpautoBlock, Matchers.notNullValue());
        assertThat(gpautoBlock, GpautoMatcher.gpautoMatcher(regionData.getLatitude(), regionData.getLongitude(), device.getValue(), precision));
    }

}
