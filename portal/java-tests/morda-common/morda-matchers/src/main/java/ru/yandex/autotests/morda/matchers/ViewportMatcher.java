package ru.yandex.autotests.morda.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class ViewportMatcher extends TypeSafeMatcher<String> {
    private static final String VIEWPORT_BEGIN = "viewport://";
    private static final String VIEWPORT_ID_KEY = "viewport_id";
    private static final String TEXT_KEY = "text";
    private StringDescription error = new StringDescription();
    private Matcher<String> viewportIdMatcher;
    private Matcher<String> textMatcher;

    public ViewportMatcher(Matcher<String> viewportIdMatcher, Matcher<String> textMatcher) {
        this.viewportIdMatcher = viewportIdMatcher;
        this.textMatcher = textMatcher;
    }

    public static ViewportMatcher viewport(Matcher<String> viewportIdMatcher, Matcher<String> textMatcher) {
        return new ViewportMatcher(viewportIdMatcher, textMatcher);
    }

    private Map<String, String> parse(String item) {
        try {
            Map<String, String> parsed = new HashMap<>();
            for (String part : item.substring(VIEWPORT_BEGIN.length() + 1).split("&")) {
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
        if (item == null || !item.startsWith(VIEWPORT_BEGIN)) {
            error.appendText("NOT A viewport URL: ").appendValue(item);
            return false;
        }

        Map<String, String> parsed = parse(item);
        String text = parsed.get(TEXT_KEY);
        String viewportId = parsed.get(VIEWPORT_ID_KEY);
        boolean matches = true;

        if (!viewportIdMatcher.matches(viewportId)) {
            viewportIdMatcher.describeMismatch(viewportId, error.appendText("viewport_id "));
            matches = false;
            error.appendText(", ");
        }

        if (!textMatcher.matches(text)) {
            textMatcher.describeMismatch(text, error.appendText("text "));
            matches = false;
            error.appendText(", ");
        }

        return matches;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("viewport, ")
                .appendText("viewport_id: ").appendDescriptionOf(viewportIdMatcher)
                .appendText(", text: ").appendDescriptionOf(textMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(error.toString());
    }
}
