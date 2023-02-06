package ru.yandex.autotests.mordacom.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.auth.User;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacom.data.HeaderData.CNT_LETTERS_LINK;

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
    private HomePage homePage = new HomePage(driver);


    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Language language : CONFIG.getMordaComLangs()) {
            for (Object[] obj : CNT_LETTERS_LINK) {
                data.add(new Object[]{language, obj[0], obj[1]});
            }
        }
        return data;
    }

    private final Language language;
    private final User authUser;
    private final LinkInfo link;

    public NewMailsCountTest(Language language, User authUser, LinkInfo link) {
        this.language = language;
        this.authUser = authUser;
        this.link = link;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.logsInAs(authUser, CONFIG.getBaseURL());
    }

    @Test
    public void mailLinkWithCount() {
        user.shouldSeeLink(homePage.headerBlock.mailLink, link);
    }
}
