package ru.yandex.autotests.mordamobile.geo;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordamobile.data.GeoData.LOCATION_TEXT_MATCHER;
import static ru.yandex.autotests.utils.morda.language.Language.RU;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок региона")
@Features("Geo Block")
public class GeoTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), RU);
        user.shouldSeeElement(homePage.geoBlock);
    }

    @Test
    public void autoLocateIcon() {
        user.shouldSeeElement(homePage.geoBlock.autoLocateIcon);
    }

    @Test
    public void regionText() {
        user.shouldSeeElement(homePage.geoBlock.region);
        user.shouldSeeElementWithText(homePage.geoBlock.region, not(isEmptyOrNullString()));
    }
}
