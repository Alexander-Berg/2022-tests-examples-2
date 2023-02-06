package ru.yandex.autotests.morda.monitorings.rssnews;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.blocks.RssnewsWidget;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.terra.junit.rules.BottleMessageRule;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Rss News")
@Features("Rss News")
@RunWith(Parameterized.class)
public class RssNewsTest {
    public static final String RSSNEWS_ID = "_rssnews";
    private final Region region;
    private final String mainUrl;
    private final String newsUrl;
    private MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private WidgetSteps userWidget;
    private MainPage mainPage;

    public RssNewsTest(Region region) throws IOException {
        this.region = region;
        this.mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.firefox());
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userWidget = new WidgetSteps(driver);
        this.mainPage = new MainPage(driver);

        this.mainUrl = "https://www.yandex" + region.getDomain();
        this.newsUrl = "https://news.yandex" + region.getDomain();
    }

    @Parameterized.Parameters(name = "Rssnews in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                MOSCOW, KIEV
        ));
    }

    @Rule
    public MordaAllureBaseRule getRule() {
        return mordaAllureBaseRule
                .withRule(new BottleMessageRule(mordaAllureBaseRule.getDriver()));
    }

    @Before
    public void setUp() {
        user.initTest(mainUrl, region, region.getDomain().getNationalLanguage());
        userWidget.addWidget(mainUrl, RSSNEWS_ID);
        user.shouldSeeElement(mainPage.rssnewsWidget);

    }

    @Test
    public void rssNewsContentExists() {
        user.shouldSeeListWithSize(mainPage.rssnewsWidget.newsCategories, greaterThan(0));
        for (RssnewsWidget.NewsCategory category : mainPage.rssnewsWidget.newsCategories) {
            shouldSeeNewsCategory(category);
        }
    }

    @Step
    public void shouldSeeNewsCategory(RssnewsWidget.NewsCategory category) {
        user.shouldSeeElement(category);
        user.shouldSeeLinkLight(category.categoryLink, new LinkInfo(not(isEmptyOrNullString()), startsWith(newsUrl)));
        user.shouldSeeListWithSize(category.newsItems, greaterThan(0));
        for (RssnewsWidget.NewsItem item : category.newsItems) {
            user.shouldSeeElement(item);
            user.shouldSeeElementWithText(item.title, not(isEmptyOrNullString()));
            user.shouldSeeLinkLight(item.link, new LinkInfo(not(isEmptyOrNullString()), startsWith(newsUrl)));
        }
    }
}
