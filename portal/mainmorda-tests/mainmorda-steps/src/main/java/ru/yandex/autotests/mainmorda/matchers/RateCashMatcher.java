package ru.yandex.autotests.mainmorda.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mainmorda.blocks.RateCash;
import ru.yandex.autotests.mainmorda.data.RatesData;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class RateCashMatcher extends TypeSafeMatcher<RateCash> {

    @Override
    protected boolean matchesSafely(RateCash item) {
        return RatesData.RATE_MATCHER.matches(item.getSellValue()) &&
                RatesData.RATE_MATCHER.matches(item.getBuyValue());
    }

    @Override
    protected void describeMismatchSafely(RateCash item, Description mismatchDescription) {
        mismatchDescription.appendValue("Котировка " + item.getRateName() + " имеет неверный формат!");
    }

    @Override
    public void describeTo(Description description) {
        description.appendValue("Котировка имеет правильный формат");
    }

    public static RateCashMatcher rateCashMatcher() {
        return new RateCashMatcher();
    }

}
