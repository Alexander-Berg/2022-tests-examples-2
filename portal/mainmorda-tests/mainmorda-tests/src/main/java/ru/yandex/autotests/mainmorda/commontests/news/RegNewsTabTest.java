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

import static ru.yandex.autotests.mainmorda.data.NewsBlockData.REGION_NEWS_TEXT;

/**
 * User: alex89
 * Date: 19.04.12
 * Проверка работы "таб"-а региональных новостей  в блоке новостей.
 */
@Aqua.Test(title = "Таб Региональных новостей: перевод и ссылка")
@Features({"Main", "Common", "News Block"})
@Stories("Regional News")
public class RegNewsTabTest {
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
    }

    @Test
    public void regNewsTabIsNotSelectedByDefault() {
        user.shouldSeeElement(mainPage.newsBlock.regNewsTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.regNewsTab);
    }

    @Test
    public void regionNewsTabSelectable() {
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
    public void regionNewsTabText() {
        user.shouldSeeElementWithText(mainPage.newsBlock.regNewsTab, REGION_NEWS_TEXT);
    }

    @Test
    public void regionNewsTabLink() {
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
        user.clicksOn(mainPage.newsBlock.regNewsTab);
        user.shouldSeePage(NewsBlockData.NEWS_HTTPS_URL);
    }
}
