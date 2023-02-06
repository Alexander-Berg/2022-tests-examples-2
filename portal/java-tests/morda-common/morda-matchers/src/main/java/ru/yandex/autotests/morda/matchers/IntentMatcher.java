package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class IntentMatcher extends TypeSafeMatcher<String> {
    private static final String INTENT_BEGIN = "intent://";
    private static final String INTENT_SEPARATOR = "#Intent;";
    private static final String INTENT_END = "end;";
    private StringDescription error = new StringDescription();
    private Map<String, Matcher<String>> matchers = new HashMap<>();


    public IntentMatcher() {
    }

    public static IntentMatcher intent() {
        return new IntentMatcher();
    }

    private boolean isValidIntentUrl(String item) {
        Pattern pattern = Pattern.compile("intent://.*#Intent;.*end;");
        return (pattern.matcher(item).matches());
    }

    private Map<String, String> parse(String item) {

        try {
            Map<String, String> parsed = new HashMap<>();
            int separator = item.indexOf(INTENT_SEPARATOR);
            String url = item.substring(INTENT_BEGIN.length(), separator);
            parsed.put("url", url);

            String params = item.substring(separator + INTENT_SEPARATOR.length(), item.indexOf(INTENT_END));
            for (String part : params.split(";")) {
                String[] kv = part.split("=");
                if ("S.browser_fallback_url".equals(kv[0])) {
                    parsed.put(kv[0], URLDecoder.decode(kv[1], "UTF-8"));
                } else {
                    parsed.put(kv[0], kv[1]);
                }
            }
            return parsed;
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    public IntentMatcher url(Matcher<String> url) {
        matchers.put("url", url);
        return this;
    }

    public IntentMatcher packageMatcher(Matcher<String> packageMatcher) {
        matchers.put("package", packageMatcher);
        return this;
    }

    public IntentMatcher action(Matcher<String> action) {
        matchers.put("action", action);
        return this;
    }

    public IntentMatcher category(Matcher<String> category) {
        matchers.put("category", category);
        return this;
    }

    public IntentMatcher component(Matcher<String> component) {
        matchers.put("component", component);
        return this;
    }

    public IntentMatcher scheme(Matcher<String> scheme) {
        matchers.put("scheme", scheme);
        return this;
    }

    public IntentMatcher browserFallbackUrl(Matcher<String> fallbackUrl) {
        matchers.put("S.browser_fallback_url", fallbackUrl);
        return this;
    }

    @Override
    protected boolean matchesSafely(String item) {
        this.error = new StringDescription();
        if (item == null || !isValidIntentUrl(item)) {
            error.appendText("NOT A valid intent URL: ").appendValue(item);
            return false;
        }

        Map<String, String> parsed = parse(item);
        boolean matches = true;

        for (Map.Entry<String, Matcher<String>> entry : matchers.entrySet()) {
            Matcher<String> matcher = entry.getValue();
            String key = entry.getKey();
            String actual = parsed.get(key);
            if (!matcher.matches(actual)) {
                matcher.describeMismatch(actual, error.appendText(key + " "));
                matches = false;
                error.appendText(", ");
            }
        }

        return matches;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("intent, ");
        for (Map.Entry<String, Matcher<String>> s : matchers.entrySet()) {
            description.appendText(s.getKey()).appendText(": ").appendDescriptionOf(s.getValue()).appendText(", ");
        }
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(error.toString());
    }
}
