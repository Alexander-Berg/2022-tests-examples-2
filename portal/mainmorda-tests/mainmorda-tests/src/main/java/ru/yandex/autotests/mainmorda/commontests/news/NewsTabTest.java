package ru.yandex.autotests.mainmorda.commontests.news;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.NewsBlockData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.NewsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

/**
 * User: alex89
 * Date: 17.04.12
 * Проверка работы "таб"-а "НОВОСТИ"  в блоке новостей.
 */
@Aqua.Test(title = "Таб Главных новостей: перевод и ссылка")
@Features({"Main", "Common", "News Block"})
@Stories("Main News")
public class NewsTabTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private NewsSteps userNews = new NewsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.newsBlock);
        user.shouldSeeElement(mainPage.newsBlock.mainNewsTab);
    }

    @Test
    public void newsTabIsSelectedByDefault() {
        user.shouldSeeElementIsSelected(mainPage.newsBlock.mainNewsTab);
    }

    @Test
    public void newsTabSelectable() {
        user.shouldSeeElement(mainPage.newsBlock.regNewsTab);
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
        user.shouldSeeElementIsSelected(mainPage.newsBlock.regNewsTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.mainNewsTab);

        user.shouldSeeElement(mainPage.newsBlock.mainNewsTab);
        userNews.switchToTab(mainPage.newsBlock.mainNewsTab);
        user.shouldSeeElementIsSelected(mainPage.newsBlock.mainNewsTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.regNewsTab);
    }

    @Test
    public void newsTabText() {
        user.shouldSeeElementWithText(mainPage.newsBlock.mainNewsTab, NewsBlockData.NEWS_TEXT);
    }

    @Test
    public void newsTabLink() {
        userNews.switchToTab(mainPage.newsBlock.mainNewsTab);
        user.clicksOn(mainPage.newsBlock.mainNewsTab);
        user.shouldSeePage(NewsBlockData.NEWS_HTTPS_URL);
    }
}