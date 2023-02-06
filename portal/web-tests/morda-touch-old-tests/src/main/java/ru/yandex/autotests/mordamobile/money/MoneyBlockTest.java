package ru.yandex.autotests.mordamobile.money;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.MoneyData.MONEY_BLOCK_REGIONS;
import static ru.yandex.autotests.mordamobile.data.MoneyData.MONEY_LINK;
import static ru.yandex.autotests.mordamobile.data.MoneyData.MONEY_TITLE;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_MONEY;

/**
 * User: ivannik
 * Date: 09.01.14
 * Time: 14:38
 */
@Aqua.Test(title = "Блок денег")
@RunWith(Parameterized.class)
@Features("Money")
public class MoneyBlockTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return MONEY_BLOCK_REGIONS;
    }

    public MoneyBlockTest(Region region, Matcher<String> moneyTextMatcher) {
        this.region = region;
        this.moneyTextMatcher = moneyTextMatcher;
    }

    private Region region;
    private Matcher<String> moneyTextMatcher;

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), region, CONFIG.getLang());
        user.logsInAs(NEW_MONEY, CONFIG.getBaseURL());
        user.shouldSeeElement(homePage.moneyBlock);
    }

    @Test
    public void moneyTitle() {
        user.shouldSeeElement(homePage.moneyBlock.title);
        user.shouldSeeElementWithText(homePage.moneyBlock.title, MONEY_TITLE);
    }

    @Test
    public void moneyIcon() {
        user.shouldSeeElement(homePage.moneyBlock.icon);
    }

    @Test
    public void moneyNumber() {
        user.shouldSeeElement(homePage.moneyBlock.numMoney);
        user.shouldSeeElementWithText(homePage.moneyBlock.numMoney, moneyTextMatcher);
    }

    @Test
    public void moneyLink() {
        user.shouldSeeLink(homePage.moneyBlock.moeneyLink, MONEY_LINK);
    }
}
