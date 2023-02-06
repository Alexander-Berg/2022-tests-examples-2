package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.TestFailedFlag;
import ru.yandex.qatools.htmlelements.matchers.decorators.MatcherDecoratorsBuilder;

import static org.hamcrest.Matchers.is;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;
import static ru.yandex.qatools.htmlelements.matchers.decorators.MatcherDecoratorsBuilder.should;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class WithWaitForMatcher {
    private static final long TIMEOUT = 5000;

    public static <T> MatcherDecoratorsBuilder withWaitFor(Matcher<? super T> matcher) {
        return should(matcher).whileWaitingUntil(timeoutHasExpired(TIMEOUT))
                .inCase(TestFailedFlag.notFailed(), is(true));
    }
}
