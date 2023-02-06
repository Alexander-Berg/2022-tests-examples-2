package ru.yandex.autotests.mainmorda.commontests.geoblock;

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

import static ru.yandex.autotests.mainmorda.data.GeoIconsData.CITY_ADAPTIVE_TEST_LIST;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.DEFAULT_SIZE;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.SMALL_SIZE;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03.04.13
 */
@Aqua.Test(title = "Адаптивность")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Geo Block"})
@Stories("Adaptive Icons")
public class AdaptiveIconsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CITY_ADAPTIVE_TEST_LIST);
    }

    private CityGeoInfo data;

    public AdaptiveIconsTest(CityGeoInfo data) {
        this.data = data;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.setsRegion(data.getRegion());
        user.resizeWindow(DEFAULT_SIZE);
    }

    @Test
    public void adaptiveIcons() {
        user.shouldSeeElement(mainPage.geoBlock.adaptiveIcon);
        user.shouldNotSeeElement(mainPage.geoBlock.adaptiveLink);
        user.resizeWindow(SMALL_SIZE);
        user.shouldNotSeeElement(mainPage.geoBlock.adaptiveIcon);
        user.shouldSeeElement(mainPage.geoBlock.adaptiveLink);
        user.resizeWindow(DEFAULT_SIZE);
        user.shouldSeeElement(mainPage.geoBlock.adaptiveIcon);
        user.shouldNotSeeElement(mainPage.geoBlock.adaptiveLink);
    }

}
