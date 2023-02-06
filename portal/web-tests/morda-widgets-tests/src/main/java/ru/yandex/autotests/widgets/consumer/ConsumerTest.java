package ru.yandex.autotests.widgets.consumer;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.autotests.widgets.steps.ConsumerSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.widgets.data.ConsumerData.CONSUMER_LINK;
import static ru.yandex.autotests.widgets.data.ConsumerData.CONSUMER_URL;

/**
 * User: leonsabr
 * Date: 29.11.11
 */
@Aqua.Test(title = "Параметр consumer сохраняется при поиске и навигации по каталогу")
@Features("Consumer")
public class ConsumerTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ConsumerSteps userConsumer = new ConsumerSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.opensPage(CONSUMER_URL);
    }

    @Test
    public void categories() {
        user.shouldSeeListWithSize(widgetPage.allCategories, greaterThan(0));
        userConsumer.shouldSeeConsumerInCategories(widgetPage.allCategories);
    }

    @Test
    public void tags() {
        user.shouldSeeListWithSize(widgetPage.allTags, greaterThan(0));
        userConsumer.shouldSeeConsumerInLinks(widgetPage.allTags);
    }

    @Test
    public void regions() {
        user.shouldSeeListWithSize(widgetPage.allRegions, greaterThan(0));
        userConsumer.shouldSeeConsumerInLinks(widgetPage.allRegions);
    }


    @Test
    public void pager() {
        userConsumer.shouldSeeConsumerInPager();
    }

    @Test
    public void search() {
        user.shouldSeeElement(widgetPage.searchField);
        user.entersTextInInput(widgetPage.searchField, "yandex");
        user.shouldSeeElement(widgetPage.searchButton);
        user.clicksOn(widgetPage.searchButton);
        user.shouldSeePage(CONSUMER_LINK.url);
    }
}
