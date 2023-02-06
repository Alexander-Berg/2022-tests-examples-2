package ru.yandex.autotests.mainmorda.commontests.geoblock;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.steps.GeoIconsSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.utils.CityGeoInfo;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mainmorda.data.GeoIconsData.CITY_OBJECTS_LIST;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.SMALL_SIZE;

/**
 * User: lipka
 * Date: 25.04.13
 * Time: 1:53
 */
@Aqua.Test(title = "Ссылки геоблока")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Geo Block"})
@Stories("Geo Links")
public class GeoLinksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private GeoIconsSteps userGeo = new GeoIconsSteps(driver);

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> testData() {
        List<Object[]> pairs = new ArrayList<Object[]>() {
        };
        for (CityGeoInfo cityInfo : CITY_OBJECTS_LIST) {
            for (LinkInfo link : cityInfo.linkList) {
                pairs.add(new Object[]{cityInfo.region, link});
            }
        }
        return pairs;

    }

    private Region region;
    private LinkInfo link;

    public GeoLinksTest(Region region, LinkInfo link) {
        this.region = region;
        this.link = link;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.setsRegion(region);
        user.resizeWindow(SMALL_SIZE);
    }

    @Test
    public void geoLink() {
        userGeo.shouldSeeGeoLink(link);
    }
}
