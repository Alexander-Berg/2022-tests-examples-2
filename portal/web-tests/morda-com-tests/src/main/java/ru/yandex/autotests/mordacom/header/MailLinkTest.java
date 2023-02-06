package ru.yandex.autotests.mordacom.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.data.HeaderData;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.auth.User.COM_DEFAULT;

/**
 * User: alex89
 * Date: 11.10.12
 */

@Aqua.Test(title = "Проверка ссылки на почту в header-е")
@Features("Header")
@Stories("Mail Link")
@RunWith(Parameterized.class)
public class MailLinkTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public MailLinkTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.headerBlock);
    }

    @Test
    public void loginLink() {
        user.shouldSeeLinkLight(homePage.headerBlock.mailLink,
                HeaderData.getMailLink(language));
    }

    @Test
    public void passportLink() {
        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
        user.shouldSeeLinkLight(homePage.headerBlock.loginNameLink, new LinkInfo(
                equalTo(COM_DEFAULT.getLogin()),
                equalTo(HeaderData.PASSPORT_MODE_HREF + "passport"),
                hasAttribute(HREF, equalTo(HeaderData.PASSPORT_HREF))
        ));
    }

    @Test
    public void exitLink() {
        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
        user.shouldSeeLinkLight(homePage.headerBlock.exitLink,
                HeaderData.getLogoutLink(language));
    }
}

