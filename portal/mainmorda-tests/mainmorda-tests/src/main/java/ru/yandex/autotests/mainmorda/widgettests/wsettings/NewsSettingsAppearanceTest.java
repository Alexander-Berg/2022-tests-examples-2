package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.NewsSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.NewsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 24.12.12
 */
@Aqua.Test(title = "Внешний вид настроек новостей")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("News")
public class NewsSettingsAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private NewsSteps userNews = new NewsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.newsBlock);
        user.clicksOn(mainPage.newsBlock.editIcon);
        user.shouldSeeElement(mainPage.newsSettings);
    }

    @Test
    public void enumerationSelect() {
        user.shouldSeeElement(mainPage.newsSettings.enumerationSelectLabel);
        user.shouldSeeElementWithText(mainPage.newsSettings.enumerationSelectLabel,
                NewsSettingsData.ENUMERATION_TEXT);
        userNews.shouldSeeEnumerationOptionsText();
    }

    @Test
    public void languageSelect() {
        assumeTrue(CONFIG.getBaseDomain().equals(Domain.UA));
        user.shouldSeeElement(mainPage.newsSettings.languageSelectLabel);
        user.shouldSeeElementWithText(mainPage.newsSettings.languageSelectLabel,
                NewsSettingsData.LANGUAGE_TEXT);
        userNews.shouldSeeLanguageOptionsText();
    }
}
