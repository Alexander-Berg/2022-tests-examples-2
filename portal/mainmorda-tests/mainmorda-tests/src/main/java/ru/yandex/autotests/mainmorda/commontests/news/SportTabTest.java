package ru.yandex.autotests.mainmorda.commontests.news;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.NewsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.NewsBlockData.SPORT_TEXT;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.BLOGS_URL;

/**
 * User: leonsabr
 * Date: 13.04.12
 * Проверка работы "таб"-а "Блоги"  в блоке новостей.
 */
@Aqua.Test(title = "Таб Блоги-Спорт: перевод и ссылка")
@Features({"Main", "Common", "News Block"})
@Stories("Sport")
public class SportTabTest {
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
        userNews.ifSportPresent();
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.newsBlock);
    }

    @Test
    public void blogsTabIsNotSelectedByDefault() {
        user.shouldSeeElement(mainPage.newsBlock.sportTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.sportTab);
    }

    @Test
    public void blogsTabSelectable() {
        user.shouldSeeElement(mainPage.newsBlock.sportTab);
        userNews.switchToTab(mainPage.newsBlock.sportTab);
        user.shouldSeeElementIsSelected(mainPage.newsBlock.sportTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.mainNewsTab);

        user.shouldSeeElement(mainPage.newsBlock.mainNewsTab);
        userNews.switchToTab(mainPage.newsBlock.mainNewsTab);
        user.shouldSeeElementIsSelected(mainPage.newsBlock.mainNewsTab);
        user.shouldSeeElementIsNotSelected(mainPage.newsBlock.sportTab);
    }

    @Test
    public void blogsTabText() {
        user.shouldSeeElement(mainPage.newsBlock.sportTab);
        user.shouldSeeElementWithText(mainPage.newsBlock.sportTab, SPORT_TEXT);
    }

    @Test
    public void blogsTabLink() {
        user.shouldSeeElement(mainPage.newsBlock.sportTab);
        userNews.switchToTab(mainPage.newsBlock.sportTab);
        user.clicksOn(mainPage.newsBlock.sportTab);
        user.shouldSeePage(BLOGS_URL);
    }
}
