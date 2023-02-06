package ru.yandex.autotests.morda.rules.retry;

import org.apache.log4j.Logger;
import org.hamcrest.Matcher;
import org.junit.rules.TestRule;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.concurrent.TimeUnit;

import static java.lang.Math.max;
import static org.hamcrest.Matchers.either;
import static org.hamcrest.Matchers.instanceOf;

public class RetryRule implements TestRule {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    private static final Logger LOG = Logger.getLogger(RetryRule.class);
    private Matcher<Object> exceptionMatcher;
    private int attempts;
    private int delay;
    private TimeUnit timeUnit;

    private RetryRule() {
        this.attempts = max(CONFIG.getRetryCount(), 0) + 1;
        this.delay = max(CONFIG.getRetryDelay(), 0);
        this.timeUnit = TimeUnit.MILLISECONDS;
    }

    public static RetryRule retry() {
        return new RetryRule();
    }

    public RetryRule every(int delay, TimeUnit timeUnit) {
        this.timeUnit = timeUnit;
        this.delay = delay;
        return this;
    }

    public RetryRule times(int attempts) {
        this.attempts = max(attempts, 0) + 1;
        return this;
    }

    @SuppressWarnings("unchecked")
    public RetryRule ifException(Matcher<?> newMatcher) {
        exceptionMatcher = exceptionMatcher == null
                ? (Matcher<Object>) newMatcher
                : either(exceptionMatcher).or((Matcher<Object>) newMatcher);
        return this;
    }

    public RetryRule ifException(Class<? extends Throwable> type) {
        return ifException(instanceOf(type));
    }

    @Override
    public Statement apply(final Statement base, final Description description) {
        return new Statement() {
            @Override
            public void evaluate() throws Throwable {
                if (attempts > 1) {
                    Throwable error = null;
                    for (int i = 0; i < attempts; i++) {
                        if ((error = iteration(base, i + 1)) == null) {
                            return;
                        }
                        if (i < attempts) {
                            LOG.info("Sleeping for " + delay + " " + timeUnit.name() + " to retry...");
                            Thread.sleep(timeUnit.toMillis(delay));
                        }
                    }
                    LOG.info("All [" + attempts + "] attempts failed");
                    throw error;
                } else {
                    base.evaluate();
                }
            }
        };
    }

    @Step(value = "******* Attempt {1} *******")
    public Throwable iteration(Statement base, int attempt) throws Throwable {
        try {
            LOG.info("Starting attempt [" + attempt + "]");
            base.evaluate();
            return null;
        } catch (Throwable e) {
            LOG.info("Attempt [" + attempt + "] failed");
            if (exceptionMatcher == null || exceptionMatcher.matches(e)) {
                return e;
            } else {
                throw e;
            }
        }
    }
}
