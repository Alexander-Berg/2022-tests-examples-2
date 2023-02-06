package ru.yandex.autotests.mordacommonsteps.rules;

import org.hamcrest.Matcher;
import org.junit.internal.matchers.TypeSafeMatcher;
import org.junit.rules.TestRule;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.concurrent.TimeUnit;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.matchers.JUnitMatchers.containsString;
import static org.junit.matchers.JUnitMatchers.either;


/**
* Usage:   
*    @Rule 
*    public RetryRule retry = RetryRule.retry().ifException(WebdriverAssertionError.class) 
*    .every(20, TimeUnit.SECONDS).times(2); 
*/ 
public class RetryRule implements TestRule { 
 
    private Matcher<Object> matcher; 
    private int attempts = 3; 
    private int delay = 10; 
    private TimeUnit timeUnit = TimeUnit.SECONDS; 
 
    private RetryRule() { 
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
        this.attempts = attempts; 
        return this; 
    } 

    @SuppressWarnings("unchecked") 
    public RetryRule ifException(Matcher<?> newMatcher) { 
        if (matcher == null) 
            matcher = (Matcher<Object>) newMatcher; 
        else 
            matcher = either(matcher).or((Matcher<Object>) newMatcher);
        return this; 
    } 
 
    /** 
     * Adds to the list of requirements for any thrown exception that it 
     * should be an instance of {@code type} 
     */ 
    public RetryRule ifException(Class<? extends Throwable> type) { 
        return ifException(instanceOf(type)); 
    } 
 
    /** 
     * Adds to the list of requirements for any thrown exception that it 
     * should <em>contain</em> string {@code substring} 
     */ 
    public RetryRule ifMessage(String substring) { 
        return ifMessage(containsString(substring)); 
    } 
 
    /** 
     * Adds {@code matcher} to the list of requirements for the message 
     * returned from any thrown exception. 
     */ 
    public RetryRule ifMessage(Matcher<String> matcher) { 
        return ifException(hasMessage(matcher)); 
    } 
 
    public RetryRule or() { 
        return this; 
    } 

    @Override 
    public Statement apply(final Statement base, final Description description) { 
        return new Statement() { 
            @Override 
            public void evaluate() throws Throwable {
                if (attempts > 0) {
                    Throwable e = null;
                    for (int i = 0; i <= attempts; i++) {
                        try {
                            iteration(i + 1, base);
                            return;
                        } catch (Throwable t) {
                            e = t;
                            if (matcher != null && matcher.matches(e)) {
                                System.out.println("Attempt [" + i + "] failed, sleeping for "
                                        + delay + " " + timeUnit.name() + " to retry...");
                                Thread.sleep(timeUnit.toMillis(delay));
                            } else {
                                throw e;
                            }
                        }
                    }
                    System.out.println("All [" + attempts + "] attempts failed, forgiving...");
                    throw e;
                } else {
                    base.evaluate();
                }

            } 
        }; 
    } 
 
    private Matcher<Throwable> hasMessage(final Matcher<String> matcher) { 
        return new TypeSafeMatcher<Throwable>() { 
            public void describeTo(org.hamcrest.Description description) { 
                description.appendText("exception with message "); 
                description.appendDescriptionOf(matcher); 
            } 
 
            @Override 
            public boolean matchesSafely(Throwable item) { 
                return matcher.matches(item.getMessage()); 
            } 
        }; 
    }

    @Step(value = "******* Attempt {0} *******")
    public void iteration(int n, Statement base) throws Throwable {
        try {
            base.evaluate();
        } catch (Throwable throwable) {
            error(throwable.getMessage());
            throw throwable;
        }
    }

    @Step(value = "ERROR: \"{0}\"")
    public void error(String error){
        System.out.println(error);
    }
} 
