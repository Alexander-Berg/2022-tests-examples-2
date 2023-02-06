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
public class YellowskinMatcher extends TypeSafeMatcher<String> {
    private static final String YELLOWSKIN_BEGIN = "yellowskin://";
    private static final String PRIMARY_COLOR_KEY = "primary_color";
    private static final String SECONDARY_COLOR_KEY = "secondary_color";
    private static final String URL_KEY = "url";
    private StringDescription error = new StringDescription();
    private Matcher<String> primaryColorMatcher;
    private Matcher<String> secondaryColorMatcher;
    private Matcher<String> urlMatcher;

    public YellowskinMatcher(String primaryColor, String secondaryColor, Matcher<String> urlMatcher) {
        this.primaryColorMatcher = equalTo(primaryColor);
        this.secondaryColorMatcher = equalTo(secondaryColor);
        this.urlMatcher = urlMatcher;
    }

    public static YellowskinMatcher yellowskin(String primaryColor, String secondaryColor, Matcher<String> urlMatcher) {
        return new YellowskinMatcher(primaryColor, secondaryColor, urlMatcher);
    }

    private Map<String, String> parse(String item) {
        try {
            Map<String, String> parsed = new HashMap<>();
            for (String part : item.substring(YELLOWSKIN_BEGIN.length() + 1).split("&")) {
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
        if (item == null || !item.startsWith(YELLOWSKIN_BEGIN)) {
            error.appendText("NOT A yellowskin URL: ").appendValue(item);
            return false;
        }

        Map<String, String> parsed = parse(item);
        String primaryColor = parsed.get(PRIMARY_COLOR_KEY);
        String secondaryColor = parsed.get(SECONDARY_COLOR_KEY);
        String url = parsed.get(URL_KEY);
        boolean matches = true;

        if (!primaryColorMatcher.matches(primaryColor)) {
            primaryColorMatcher.describeMismatch(primaryColor, error.appendText("primary_color "));
            matches = false;
            error.appendText(", ");
        }

        if (!secondaryColorMatcher.matches(secondaryColor)) {
            secondaryColorMatcher.describeMismatch(secondaryColor, error.appendText("secondary_color "));
            matches = false;
            error.appendText(", ");
        }
        if (!urlMatcher.matches(url)) {
            urlMatcher.describeMismatch(url, error.appendText("url ("));
            error.appendText(")");
            matches = false;
        }

        return matches;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("yellowskin, ")
                .appendText("primary_color: ").appendDescriptionOf(primaryColorMatcher)
                .appendText(", secondary_color: ").appendDescriptionOf(secondaryColorMatcher)
                .appendText(", url: (").appendDescriptionOf(urlMatcher).appendText(")");
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(error.toString());
    }
}
