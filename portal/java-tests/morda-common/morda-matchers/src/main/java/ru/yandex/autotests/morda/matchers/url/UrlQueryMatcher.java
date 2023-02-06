package ru.yandex.autotests.morda.matchers.url;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.joining;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public class UrlQueryMatcher extends TypeSafeMatcher<String> {
    private static final Pattern QUERY_PATTERN = Pattern.compile("[A-Za-z0-9\\-\\._~%!$&'\\(\\)\\*\\+,;=:@\\?\\/]*");
    private Map<String, Matcher<? super String>> queryMatchers = new HashMap<>();
    private Map<String, String> parsed;
    private List<String> badParams;
    private boolean checkEncoding;

    public UrlQueryMatcher() {
        this(false);
    }

    public UrlQueryMatcher(boolean checkEncoding) {
        this.checkEncoding = checkEncoding;
    }

    public static UrlQueryMatcher queryMatcher() {
        return new UrlQueryMatcher();
    }

    public static UrlQueryMatcher queryMatcher(boolean encoded) {
        return new UrlQueryMatcher(encoded);
    }

    public static UrlQueryMatcher queryMatcher(String query) {
        UrlQueryMatcher queryMatcher = new UrlQueryMatcher();
        parseQuery(query).entrySet().forEach(e -> queryMatcher.param(e.getKey(), e.getValue()));
        return queryMatcher;
    }

    private static Map<String, String> parseQuery(String query) {
        Map<String, String> parsed = new HashMap<>();
        if (query != null && !query.isEmpty()) {
            for (String part : query.split("&")) {
                if (part == null || part.isEmpty() || !part.matches(".+=.*")) {
                    throw new IllegalArgumentException("Failed to parse query \"" + query + "\". Bad part: \"" + part + "\"");
                }
                String[] param = part.split("=");
                if (param.length != 2) {
                    parsed.put(param[0], "");
                } else {
                    parsed.put(param[0], param[1]);
                }
            }
        }
        return parsed;
    }

    public UrlQueryMatcher encoded() {
        this.checkEncoding = true;
        return this;
    }

    public UrlQueryMatcher param(String key, String value) {
        return param(key, equalTo(value));
    }

    public UrlQueryMatcher param(String key, Matcher<? super String> value) {
        this.queryMatchers.put(key, value);
        return this;
    }

    public UrlQueryMatcher paramOrNull(String key, String value) {
        return paramOrNull(key, equalTo(value));
    }

    public UrlQueryMatcher paramOrNull(String key, Matcher<? super String> value) {
        return param(key, anyOf(isEmptyOrNullString(), value));
    }

    @Override
    protected boolean matchesSafely(String item) {
        URI uri = URI.create(item);
        parsed = parseQuery(uri.getRawQuery());
        badParams = queryMatchers.entrySet().stream()
                .filter(e -> !e.getValue().matches(parsed.get(e.getKey())))
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
        if (checkEncoding) {
            return badParams.isEmpty() && isValidEncoding(item);
        } else {
            return badParams.isEmpty();
        }
    }

    private boolean isValidEncoding(String item) {
        String query = URI.create(item).getRawQuery();
        if (query == null) {
            return true;
        }
        return QUERY_PATTERN.matcher(query).matches();
    }

    @Override
    public void describeTo(Description description) {
        if (queryMatchers.isEmpty() && !checkEncoding) {
            return;
        }
        List<String> checks = new ArrayList<>();
        if (checkEncoding) {
            checks.add("encoded");
        }
        queryMatchers.entrySet().forEach(e -> checks.add("\"" + e.getKey() + "\": " + e.getValue().toString()));
        description.appendText("query [")
                .appendText(checks.stream().collect(joining(", ")))
                .appendText("]");
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        if (queryMatchers.isEmpty() && !checkEncoding) {
            return;
        }

        List<String> errors = new ArrayList<>();
        if (checkEncoding && !isValidEncoding(item)) {
            errors.add("bad encoding");
        }
        badParams.forEach(e -> errors.add("\"" + e + "\" was \"" + parsed.get(e) + "\""));

        mismatchDescription.appendText("in query [")
                .appendText(errors.stream().collect(joining(", ")))
                .appendText("]");
    }
}
