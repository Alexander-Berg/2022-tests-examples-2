package ru.yandex.autotests.mainmorda.matchers;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.mainmorda.blocks.RateCurrency;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class RateCurrencyMatcher extends TypeSafeMatcher<RateCurrency> {
    private final HtmlElement tomorrow;
    private static final double EPS = 0.004;

    public RateCurrencyMatcher(HtmlElement tomorrow) {
        this.tomorrow = tomorrow;
    }

    @Override
    protected boolean matchesSafely(RateCurrency item) {
        if (tomorrow.getText().isEmpty()) {
            return matchesNoTomorrow(item);
        } else {
            if (item.getTomorrowValue().isEmpty()) {
                return matchesNoTomorrow(item);
            } else {
                double expectedDiff = Double.parseDouble(item.getTomorrowValue().replace(',', '.')) -
                        Double.parseDouble(item.getTodayValue().replace(',', '.'));
                double diff = Double.parseDouble(item.getDiff().replace(',', '.').replace('−', '-'));
                return matchesAllWithDiffAccuracy(item, Math.abs(diff - expectedDiff));
            }
        }
    }

    private boolean matchesNoTomorrow(RateCurrency item) {
        return RatesData.RATE_MATCHER.matches(item.getTodayValue()) &&
                item.getDiff().isEmpty() && item.getTomorrowValue().isEmpty();
    }

    private boolean matchesAllWithDiffAccuracy(RateCurrency item, double accuracy) {
        return matchesAll(item) && accuracy < EPS;
    }

    private boolean matchesAll(RateCurrency item) {
        return RatesData.RATE_MATCHER.matches(item.getTodayValue()) &&
                RatesData.RATE_DIFF_MATCHER.matches(item.getDiff()) &&
                RatesData.RATE_MATCHER.matches(item.getTomorrowValue());
    }

    @Override
    public void describeTo(Description description) {
        description.appendValue("Котировка имеет правильный формат");
    }

    @Override
    protected void describeMismatchSafely(RateCurrency item, Description mismatchDescription) {
        mismatchDescription.appendValue("Котировка " + item.getRateName() + " имеет неверный формат!");
    }

    public static RateCurrencyMatcher rateCurrencyMatcher(HtmlElement tomorrow) {
        return new RateCurrencyMatcher(tomorrow);
    }

}
