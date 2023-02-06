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

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.DEFAULT_NEWS_SIZE;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.NEWS_LANGUAGE;

/**
 * User: alex89
 * Date: 19.04.12
 * Проверка списка региональных новостей и ссылок
 */
@Aqua.Test(title = "Региональные события")
@Features({"Main", "Common", "News Block"})
@Stories("Regional News")
public class RegNewsItemsTest {
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
        user.shouldSeeElement(mainPage.newsBlock.regNewsTab);
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
    }

    @Test
    public void regionalNewsNumber() {
        user.shouldSeeListWithSize(mainPage.newsBlock.regionalNews, equalTo(DEFAULT_NEWS_SIZE));
    }

    @Test
    public void regionalNewsNumerationByDefault() {
        userNews.shouldSeeNumeration(mainPage.newsBlock.regionalNews);
    }

    @Test
    public void regionalNewsHaveCorrectSymbols() {
        userNews.shouldSeeLanguage(mainPage.newsBlock.regionalNews, NEWS_LANGUAGE);
    }

    @Test
    public void noRegionalNewsDuplicates() {
        userNews.shouldNotSeeDuplicates(userNews.getNewsTexts(mainPage.newsBlock.regionalNews));
    }

    @Test
    public void regionalNewsLinks() {
        userNews.shouldSeeLinks(mainPage.newsBlock.regNewsTab,
                mainPage.newsBlock.regionalNews, NewsBlockData.NEWS_LINK);
    }
}