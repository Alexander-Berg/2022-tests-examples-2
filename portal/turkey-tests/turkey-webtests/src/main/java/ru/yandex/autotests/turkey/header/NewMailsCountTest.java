package ru.yandex.autotests.turkey.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.utils.morda.auth.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.HeaderData.CNT_LETTERS_LINK;

/**
 * User: ivannik
 * Date: 13.06.13
 * Time: 14:44
 */
@Aqua.Test(title = "Ссылки с количеством непрочитанных сообщений")
@RunWith(Parameterized.class)
@Features("Header")
@Stories("New Messages Count")
public class NewMailsCountTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);


    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return CNT_LETTERS_LINK;
    }

    private User authUser;
    private LinkInfo link;

    public NewMailsCountTest(User authUser, LinkInfo link) {
        this.authUser = authUser;
        this.link = link;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.logsInAs(authUser, CONFIG.getBaseURL());
    }

    @Test
    public void mailLinkWithCount() {
        user.shouldSeeLink(yandexComTrPage.headerBlock.mailLink, link);
    }
}
