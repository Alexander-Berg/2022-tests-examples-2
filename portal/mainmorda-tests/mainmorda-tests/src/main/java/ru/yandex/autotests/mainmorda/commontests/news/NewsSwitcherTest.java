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

import java.util.List;

/**
 * User: alex89
 * Date: 19.04.12
 * Проверка переключения списка при переключении "табов". (В блоке новостей).
 * И того, что нумерация не исчезает при переключении
 */
@Aqua.Test(title = "Переключение вкладок")
@Features({"Main", "Common", "News Block"})
@Stories("Switcher")
public class NewsSwitcherTest {
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
    public void newsDifferFromSport() {
        userNews.ifSportPresent();
        List<String> news = userNews.getNewsTexts(mainPage.newsBlock.mainNews);
        userNews.switchToTab(mainPage.newsBlock.sportTab);
        List<String> blogs = userNews.getNewsTexts(mainPage.newsBlock.sportNews);
        userNews.shouldBeDifferent(news, blogs);
    }

    @Test
    public void regionalNewsDifferFromSport() {
        userNews.ifSportPresent();
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
        List<String> news = userNews.getNewsTexts(mainPage.newsBlock.regionalNews);
        userNews.switchToTab(mainPage.newsBlock.sportTab);
        List<String> blogs = userNews.getNewsTexts(mainPage.newsBlock.sportNews);
        userNews.shouldBeDifferent(news, blogs);
    }

    @Test
    public void newsDifferFromRegionalNews() {
        List<String> news = userNews.getNewsTexts(mainPage.newsBlock.mainNews);
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
        List<String> regionalNews = userNews.getNewsTexts(mainPage.newsBlock.regionalNews);
        userNews.shouldBeDifferent(news, regionalNews);
    }
}
