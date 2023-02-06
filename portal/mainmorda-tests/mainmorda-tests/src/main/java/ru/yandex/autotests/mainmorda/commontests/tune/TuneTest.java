package ru.yandex.autotests.mainmorda.commontests.tune;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TuneData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.TuneRegionPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

/**
 * User: eoff
 * Date: 29.01.13
 */
@Aqua.Test(title = "Проверка tune")
@Features({"Main", "Common", "Tune"})
@Stories("Auto Checkbox")
public class TuneTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private TuneRegionPage tuneRegionPage = new TuneRegionPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.headerBlock);
    }

    @Test
    public void autoCheckboxDeselects() {
        user.shouldSeeElement(mainPage.headerBlock.setupLink);
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupMainPopUp);
        user.shouldSeeElement(mainPage.headerBlock.setupMainPopUp.changeCityLink);
        user.clicksOn(mainPage.headerBlock.setupMainPopUp.changeCityLink);
        user.shouldSeePage(TuneData.TUNE_URL_PATTERN.replace("%s", CONFIG.getBaseDomain().toString()));
        user.shouldSeeElementIsSelected(tuneRegionPage.auto);
        user.clearsInput(tuneRegionPage.input);
        user.shouldSeeElementIsNotSelected(tuneRegionPage.auto);

    }
}
