package ru.yandex.autotests.turkey.redirect;

import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.TuneRedirectPage;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.HashSet;

import static java.lang.Thread.sleep;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: lipka
 * Date: 22.05.13
 */
@Aqua.Test(title = "Редирект на турецкую морду с турецким ip")
@Features("Redirect")
public class RedirectTest {
    private static final Properties CONFIG = new Properties();
    public static final String COM_IP_URL = CONFIG.getBaseURL().replace(".tr", "") + "/";
    public static final String TUNE_REDIRECT_URL = "https://yandex.com/tune/redirect";
    public static final String ANKARA_IP = "78.160.131.103";

    private MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();
    @Rule
    public MordaAllureBaseRule rule() throws Exception {
        return mordaAllureBaseRule.mergeProxyAction(HeaderAction.class,
                        new HashSet<>(asList(new Header("X-Forwarded-For", ANKARA_IP))));
    }

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private TuneRedirectPage tuneRedirectPage = new TuneRedirectPage(driver);

    @Test
    public void redirect() {
        user.opensPage(COM_IP_URL, CONFIG.getBaseURL());
        user.shouldSeePage(CONFIG.getBaseURL());
    }

    @Test
    public void tuneRedirectOff() throws InterruptedException {
        user.opensPage(TUNE_REDIRECT_URL);
        user.clicksOn(tuneRedirectPage.redirectCheckbox);
        user.clicksOn(tuneRedirectPage.saveButton);
        user.shouldSeePage(matches(".*yandex.*"));
        sleep(500);
        user.opensPage(COM_IP_URL);
        user.shouldSeePage(COM_IP_URL);
    }
}
