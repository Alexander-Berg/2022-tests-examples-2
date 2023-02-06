package ru.yandex.autotests.mainmorda.commontests.geoblock;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.utils.CityGeoInfo;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.CITY_OBJECTS_LIST;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.DEFAULT_SIZE;

/**
 * User: ivannik
 * Date: 05.06.13
 * Time: 14:12
 */
@Aqua.Test(title = "Количество иконок и ссылок геоблока")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Geo Block"})
@Stories("Count Elements")
public class CountGeoElementsTest {

    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CITY_OBJECTS_LIST);
    }

    private CityGeoInfo city;

    public CountGeoElementsTest(CityGeoInfo city) {
        this.city = city;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.setsRegion(city.getRegion());
        user.resizeWindow(DEFAULT_SIZE);
    }

    @Test
    public void geoIconsCount() {
        user.shouldSeeListWithSize(mainPage.geoBlock.allIcons, is(city.iconList.size()));
    }

    @Test
    public void geoLinksCount() {
        user.shouldSeeListWithSize(mainPage.geoBlock.allPermanentLinks,
                greaterThanOrEqualTo(city.linkList.size()));
    }
}
