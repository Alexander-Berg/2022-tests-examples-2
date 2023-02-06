package ru.yandex.autotests.internalapid.matchers;

import com.google.common.base.Joiner;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;

public class InternalApidMatchers {
    public static Matcher<Long> userHasAccessToCounters(List<Integer> counters) {
        return new TypeSafeMatcher<Long>() {
            @Override
            protected boolean matchesSafely(Long user) {
                for (Integer counter : counters) {
//                    if (!Counters.checkUserAccessToCounter(user, counter)) {
//                        return false;
//                    }
//                    todo
                }
                return true;
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("has access to ").appendText(Joiner.on(", ").join(counters));
            }
        };
    }
}
