package ru.yandex.autotests.mordacom.search;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.steps.YandexUidSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.core.IsNot.not;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.autotests.utils.morda.auth.User.COM_DEFAULT;

/**
 * User: leonsabr
 * Date: 04.04.12
 */
@Aqua.Test(title = "Параметр msid")
@Features("Search")
@Stories("msid")
@RunWith(Parameterized.class)
public class MsidTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexUidSteps userUid = new YandexUidSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public MsidTest(Language language) {
        this.language = language;
    }

    @Test
    public void msidLogoff() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        userUid.setsUIDWithCounters();
        user.refreshPage();
        user.shouldNotSeeElement(homePage.search.msid);
        user.shouldSeeElementMatchingTo(homePage.search.msid,
                hasAttribute(VALUE, not(isEmptyOrNullString())));
    }

    @Test
    public void msidLogin() {
        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        userUid.setsUIDWithCounters();
        user.refreshPage();
        user.shouldNotSeeElement(homePage.search.msid);
        user.shouldSeeElementMatchingTo(homePage.search.msid,
                hasAttribute(VALUE, not(isEmptyOrNullString())));
    }

}
