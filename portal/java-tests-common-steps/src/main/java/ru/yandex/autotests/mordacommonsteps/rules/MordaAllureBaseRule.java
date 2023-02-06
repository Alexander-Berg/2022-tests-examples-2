package ru.yandex.autotests.mordacommonsteps.rules;

import net.lightbody.bmp.proxy.ProxyServer;
import org.junit.internal.AssumptionViolatedException;
import org.junit.rules.RuleChain;
import org.junit.rules.TestRule;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.MordaProxyRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.ConfigProxyActions;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.MergeableProxyAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.ReplaceableProxyAction;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.users.BaseUser;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.qatools.selenium.grid.GridClientException;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.hamcrest.Matchers.instanceOf;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.core.AllOf.allOf;
import static ru.yandex.autotests.mordacommonsteps.rules.RetryRule.retry;
import static ru.yandex.qatools.matchers.decorators.MatcherDecorators.should;
import static ru.yandex.qatools.matchers.decorators.MatcherDecorators.timeoutHasExpired;

public class MordaAllureBaseRule implements TestRule {
    public static final Properties CONFIG = new Properties();
    private DesiredCapabilities caps;
    private RetryRule retryRule;
    private MordaProxyRule mordaProxyRule;
    private WebDriverRule webDriverRule;
    private RuleChain rules;
    private RuleChain additionalRules;
    private List<ProxyAction> additionalProxyActions = new ArrayList<>();
    private WebDriverProxy webDriverProxy;
    private UserManagerRule userManagerRule;
    private ConfigProxyActions configProxyActions;

    public MordaAllureBaseRule() {
        this(CONFIG.getCapabilities());
    }

    public MordaAllureBaseRule(DesiredCapabilities caps) {
        this.caps = caps;
        this.userManagerRule = new UserManagerRule();
        this.configProxyActions = new ConfigProxyActions();

        additionalRules = RuleChain.outerRule(userManagerRule);
        webDriverProxy = new WebDriverProxy();
        retryRule = retry()
                .every(CONFIG.getRetryDelay(), TimeUnit.MILLISECONDS)
                .times(CONFIG.getMaxRetries())
                .ifException(should(instanceOf(GridClientException.class)).
                        whileWaitingUntil(timeoutHasExpired(SECONDS.toMillis(CONFIG.getGridRetryDelay()))))
                .ifException(allOf(instanceOf(Throwable.class),
                        not(instanceOf(AssumptionViolatedException.class))));
    }

    @Override
    public Statement apply(Statement base, Description description) {
        mordaProxyRule = new MordaProxyRule(caps)
                .addProxyActions(additionalProxyActions)
                .addProxyActions(configProxyActions.getProxyActions());

        webDriverRule = new WebDriverRule(webDriverProxy, mordaProxyRule.getCapabilities());
        rules = RuleChain
                .outerRule(new AllureLoggingRule())
                .around(retryRule)
                .around(mordaProxyRule)
                .around(webDriverRule);

        return rules.around(additionalRules).apply(base, description);
    }

    public DesiredCapabilities getCaps() {
        return caps;
    }

    public void setCaps(DesiredCapabilities caps) {
        this.caps = caps;
    }

    public MordaAllureBaseRule withRule(TestRule rule) {
        additionalRules = additionalRules.around(rule);
        return this;
    }

    public MordaAllureBaseRule withProxyAction(ProxyAction proxyAction) {
        additionalProxyActions.add(proxyAction);
        return this;
    }

    public WebDriver getDriver() {
        return webDriverProxy;
    }

    public ProxyServer getProxyServer() {
        if (mordaProxyRule != null) {
            return mordaProxyRule.getProxyServer();
        }
        return null;
    }

    public User getUser(BaseUser baseUser) {
        return userManagerRule.getUser(baseUser);
    }

    public User getUser(UserType userType) {
        return userManagerRule.getUser(userType);
    }

    public User getUser(UserType userType, Mode mode) {
        return userManagerRule.getUser(userType, mode);
    }

    public <T> MordaAllureBaseRule mergeProxyAction(Class<? extends MergeableProxyAction<T>> clazz, T data) {
        configProxyActions.mergeWith(clazz, data);
        return this;
    }

    public <T> MordaAllureBaseRule replaceProxyAction(Class<? extends ReplaceableProxyAction<T>> clazz, T data) {
        configProxyActions.replaceWith(clazz, data);
        return this;
    }
}
