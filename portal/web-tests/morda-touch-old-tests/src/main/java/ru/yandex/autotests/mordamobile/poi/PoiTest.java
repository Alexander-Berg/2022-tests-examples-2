package ru.yandex.autotests.mordamobile.poi;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.PoiSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordamobile.data.PoiData.TITLE;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок промо")
@Features("Poi")
public class PoiTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private PoiSteps userPoi = new PoiSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.poiBlock);
    }

    @Test
    public void poiTitle() {
        user.shouldSeeElement(homePage.poiBlock.title);
        user.shouldSeeElementWithText(homePage.poiBlock.title, TITLE);
    }

    @Test
    public void poiLinksSize() {
        user.shouldSeeListWithSize(homePage.poiBlock.allItems, equalTo(4));
    }

    @Test
    public void poiIcon() {
        user.shouldSeeElement(homePage.poiBlock.icon);
    }

    @Test
    public void poiItemsIcon() {
        userPoi.shouldSeePoiItems();
    }
}
