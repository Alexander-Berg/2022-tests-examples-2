package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class MordaNavigateMatcher extends TypeSafeMatcher<String> {
    private static final String MORDA_NAVIGATE_BEGIN = "mordanavigate://";
    private static final String FALLBACK_KEY = "fallback";
    private static final String CARD_KEY = "card";
    private StringDescription error = new StringDescription();
    private Matcher<String> cardMatcher;
    private Matcher<String> fallbackMatcher;

    public MordaNavigateMatcher(Matcher<String> card, Matcher<String> fallbackMatcher) {
        this.cardMatcher = card;
        this.fallbackMatcher = fallbackMatcher;
    }

    public static MordaNavigateMatcher mordaNavigate(String card, Matcher<String> fallbackMatcher) {
        return new MordaNavigateMatcher(equalTo(card), fallbackMatcher);
    }

    private Map<String, String> parse(String item) {
        try {
            Map<String, String> parsed = new HashMap<>();
            for (String part : item.substring(MORDA_NAVIGATE_BEGIN.length() + 1).split("&")) {
                String[] kv = part.split("=");
                parsed.put(kv[0], URLDecoder.decode(kv[1], "UTF-8"));
            }
            return parsed;
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    protected boolean matchesSafely(String item) {
        this.error = new StringDescription();
        if (item == null || !item.startsWith(MORDA_NAVIGATE_BEGIN)) {
            error.appendText("NOT A mordanavigate URL: ").appendValue(item);
            return false;
        }

        Map<String, String> parsed = parse(item);
        String card = parsed.get(CARD_KEY);
        String fallback = parsed.get(FALLBACK_KEY);
        boolean matches = true;

        if (!cardMatcher.matches(card)) {
            cardMatcher.describeMismatch(card, error.appendText("card "));
            matches = false;
            error.appendText(", ");
        }

        if (!fallbackMatcher.matches(fallback)) {
            fallbackMatcher.describeMismatch(fallback, error.appendText("fallback "));
            matches = false;
            error.appendText(", ");
        }

        return matches;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("mordanavigate, ")
                .appendText("card: ").appendDescriptionOf(cardMatcher)
                .appendText(", fallback: ").appendDescriptionOf(fallbackMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(error.toString());
    }
}
