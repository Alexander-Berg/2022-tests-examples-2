package ru.yandex.autotests.morda.rules.base;

import net.lightbody.bmp.BrowserMobProxy;
import org.junit.internal.AssumptionViolatedException;
import org.junit.rules.RuleChain;
import org.junit.rules.TestRule;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.rules.proxy.MordaProxyRule;
import ru.yandex.autotests.morda.rules.proxy.actions.Action;
import ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverBlackListAction;
import ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverCookieAction;
import ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverHarAction;
import ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverHeaderAction;
import ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverRemapAction;
import ru.yandex.autotests.morda.rules.retry.RetryRule;
import ru.yandex.autotests.morda.rules.users.MordaUserManagerRule;
import ru.yandex.autotests.morda.rules.webdriver.WebDriverRule;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.instanceOf;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.core.AllOf.allOf;
import static ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverBlackListAction.webDriverBlackListAction;
import static ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverCookieAction.webDriverCookieAction;
import static ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverHarAction.webDriverHarAction;
import static ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverHeaderAction.webDriverHeaderAction;
import static ru.yandex.autotests.morda.rules.proxy.actions.webdriver.WebDriverRemapAction.webDriverRemapAction;
import static ru.yandex.autotests.morda.rules.retry.RetryRule.retry;

/**
 * User: asamar
 * Date: 04.09.2015.
 */
public class MordaBaseWebDriverRule extends TestWatcher {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    private final WebDriverCookieAction cookieAction;
    private final WebDriverHeaderAction headerAction;
    private final WebDriverHarAction harAction;
    private final WebDriverRemapAction remapAction;
    private final WebDriverBlackListAction blackListAction;
    private final List<TestRule> additionalRules;
    private RetryRule retryRule;
    private MordaProxyRule mordaProxyRule;
    private WebDriverRule webDriverRule;
    private MordaUserManagerRule userManagerRule;

    public MordaBaseWebDriverRule() {
        this(new DesiredCapabilities(CONFIG.getBrowserName(), CONFIG.getBrowserVersion(), Platform.ANY));
    }

    public MordaBaseWebDriverRule(DesiredCapabilities caps) {
        this.additionalRules = new ArrayList<>();
        this.webDriverRule = new WebDriverRule(caps);
        this.mordaProxyRule = new MordaProxyRule(caps);
        this.userManagerRule = new MordaUserManagerRule();

        this.retryRule = retry().ifException(allOf(
                instanceOf(Throwable.class),
                not(instanceOf(AssumptionViolatedException.class))
        ));

        this.cookieAction = webDriverCookieAction(this);
        this.blackListAction = webDriverBlackListAction(this);
        this.harAction = webDriverHarAction(this);
        this.headerAction = webDriverHeaderAction(this);
        this.remapAction = webDriverRemapAction(this);
    }

    public static MordaBaseWebDriverRule webDriverRule() {
        return new MordaBaseWebDriverRule();
    }

    public static MordaBaseWebDriverRule webDriverRule(DesiredCapabilities caps) {
        return new MordaBaseWebDriverRule(caps);
    }

    @Override
    public Statement apply(Statement base, Description description) {
        RuleChain rules = RuleChain
                .outerRule(retryRule)
                .around(new AllureLoggingRule())
                .around(userManagerRule)
                .around(mordaProxyRule)
                .around(webDriverRule);

        for (TestRule rule : additionalRules) {
            rules = rules.around(rule);
        }

        return rules.apply(base, description);
    }

    public WebDriverCookieAction cookie() {
        return cookieAction;
    }

    public WebDriverHeaderAction header() {
        return headerAction;
    }

    public WebDriverHarAction har() {
        return harAction;
    }

    public WebDriverRemapAction remap() {
        return remapAction;
    }

    public MordaBaseWebDriverRule userAgent(String userAgent) {
        return headerAction.userAgent(userAgent).done();
    }

    public MordaBaseWebDriverRule withRule(TestRule rule) {
        return around(rule);
    }

    public MordaBaseWebDriverRule exp(String userAgent) {
        return headerAction.exp(userAgent).done();
    }

    public MordaBaseWebDriverRule saveVars() {
        return headerAction.saveVars().done();
    }

    public WebDriverBlackListAction blacklist() {
        return blackListAction;
    }

    public MordaUserManagerRule user() {
        return userManagerRule;
    }

    public DesiredCapabilities getCaps() {
        return webDriverRule.getCaps();
    }

    public WebDriver getDriver() {
        return webDriverRule.getDriver();
    }

    public MordaBaseWebDriverRule register(Action... actions) {
        mordaProxyRule.register(actions);
        return this;
    }

    public MordaBaseWebDriverRule around(TestRule... rules) {
        additionalRules.addAll(asList(rules));
        return this;
    }

    public BrowserMobProxy getProxyServer() {
        if (mordaProxyRule != null) {
            return mordaProxyRule.getProxyServer();
        }
        return null;
    }

}
