package ru.yandex.autotests.morda.utils.matchers;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.mapping;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;

/**
 * User: asamar
 * Date: 07.08.2015.
 */
public class UrlMatcher extends TypeSafeMatcher<String> {

    private NamedMatcher<String> schemeMatcher;
    private NamedMatcher<String> hostMatcher;
    private NamedMatcher<String> pathMatcher;
    private List<ParamMatcher> paramMatchers;
    private Description describeMismatch;

    private UrlMatcher(Builder builder) {
        schemeMatcher = builder.schemeMatcher;
        pathMatcher = builder.pathMatcher;
        hostMatcher = builder.hostMatcher;
        paramMatchers = builder.paramMatchers;
        describeMismatch = new StringDescription().appendText("\n");
    }


    public static Builder urlMatcher() {
        return new Builder();
    }

    public static UrlMatcher.Builder urlMatcher(URI uri) {
        Builder builder = new Builder()
                .scheme(uri.getScheme())
                .host(uri.getHost())
                .path(uri.getPath());

        if (uri.getRawQuery() != null) {
            List<ParamMatcher> params = asList(uri.getRawQuery().split("&")).stream()
                    .map(e -> {
                        String[] splitted = e.split("=");
                        return urlParam(splitted[0], splitted[1]);
                    }).collect(Collectors.toList());
            builder.urlParams(params);
        }
        return builder;

        /*List<ParamMatcher> params = asList(uri.getRawQuery().split("&")).stream()
                .map(e -> {
                    String[] splitted = e.split("=");
                    return urlParam(splitted[0], splitted[1]);
                }).collect(Collectors.toList());

        return new Builder()
                .scheme(uri.getScheme())
                .host(uri.getHost())
                .path(uri.getPath())
                .urlParams(params);*/
    }

    public static UrlMatcher.Builder urlMatcher(String uri) {
        return urlMatcher(URI.create(uri));
    }


    @Override
    public void describeTo(Description description) {
        description.appendText("\n");
        describe(schemeMatcher, description);
        describe(hostMatcher, description);
        describe(pathMatcher, description);
        paramMatchers.forEach(pm -> describe(pm, description));
    }

    @Override
    protected boolean matchesSafely(String s) {
        final URI uri = URI.create(s);

        List<Boolean> matchResults = new ArrayList<>(asList(
                isMatches(uri.getScheme(), schemeMatcher),
                isMatches(uri.getHost(), hostMatcher),
                isMatches(uri.getPath(), pathMatcher)
        ));

        Optional<String> rawQueryOptional = Optional.ofNullable(uri.getRawQuery());
        rawQueryOptional.ifPresent(it -> {
            Map<String, List<String>> params = asList(uri.getRawQuery().split("&")).stream()
                    .filter(e -> e != null && !e.isEmpty())
                    .map(e -> {
                        if (e.equals("=")) {
                            throw new IllegalArgumentException("Failed to parse query for \"" + uri + "\": " + e);
                        }

                        if (e.endsWith("=")) {
                            return new BasicNameValuePair(e.substring(0, e.length() - 1), "");
                        }

                        String[] splitted = e.split("=", 2);
                        if (splitted.length != 2) {
                            throw new IllegalArgumentException("Failed to parse query for \"" + uri + "\": " + e);
                        }
                        return new BasicNameValuePair(splitted[0], splitted[1]);
                    })
                    .collect(groupingBy(NameValuePair::getName, HashMap::new, mapping(NameValuePair::getValue, toList())));
            paramMatchers.forEach(pm -> matchResults.add(isMatches(params.get(pm.getName()), pm)));
        });

//        if (uri.getRawQuery() != null) {
//            Map<String, List<String>> params = asList(uri.getRawQuery().split("&")).stream()
//                    .filter(e -> e != null && !e.isEmpty())
//                    .map(e -> {
//                        if (e.equals("=")) {
//                            throw new IllegalArgumentException("Failed to parse query for \"" + uri + "\": " + e);
//                        }
//
//                        if (e.endsWith("=")) {
//                            return new BasicNameValuePair(e.substring(0, e.length() - 1), null);
//                        }
//
//                        String[] splitted = e.split("=");
//                        if (splitted.length != 2) {
//                            throw new IllegalArgumentException("Failed to parse query for \"" + uri + "\": " + e);
//                        }
//                        return new BasicNameValuePair(splitted[0], splitted[1]);
//                    })
//                    .collect(groupingBy(NameValuePair::getName, HashMap::new, mapping(NameValuePair::getValue, toList())));
//            paramMatchers.forEach(pm -> matchResults.add(isMatches(params.get(pm.getName()), pm)));
//        }

        return !matchResults.stream().anyMatch(e -> !e);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(this.describeMismatch.toString());
    }

    private <T> boolean isMatches(T item, NamedMatcher<? super T> matcher) {
        if (matcher != null && !matcher.matchesSafely(item)) {
            matcher.describeMismatchSafely(item, describeMismatch);
            describeMismatch.appendText("\n");
            return false;
        }
        return true;
    }

    private <T> void describe(Matcher<T> matcher, Description description) {
        if (matcher != null) {
            matcher.describeTo(description);
            description.appendText("\n");
        }
    }

    public static class Builder {
        private NamedMatcher<String> schemeMatcher;
        private NamedMatcher<String> hostMatcher;
        private NamedMatcher<String> pathMatcher;
        private List<ParamMatcher> paramMatchers;

        public Builder() {
            this.paramMatchers = new ArrayList<>();
        }

        public Builder scheme(String scheme) {
            return scheme(Matchers.equalToIgnoringCase(scheme));
        }

        public Builder host(String host) {
            return host(Matchers.equalToIgnoringCase(host));
        }

        public Builder path(String path) {
            return path(Matchers.equalToIgnoringCase(path));
        }

        public Builder scheme(Matcher<String> schemeMatcher) {
            this.schemeMatcher = new NamedMatcher<>("scheme", schemeMatcher);
            return this;
        }

        public Builder host(Matcher<String> hostMatcher) {
            this.hostMatcher = new NamedMatcher<>("host", hostMatcher);
            return this;
        }

        public Builder path(Matcher<String> pathMatcher) {
            this.pathMatcher = new NamedMatcher<>("path", pathMatcher);
            return this;
        }

        public Builder urlParams(List<ParamMatcher> params) {
            this.paramMatchers.addAll(params);
            return this;
        }

        public Builder urlParams(ParamMatcher... params) {
            return urlParams(asList(params));
        }

        public UrlMatcher build() {
            return new UrlMatcher(this);
        }
    }

    public static class ParamMatcher extends NamedMatcher<Iterable<? super String>> {
        private Matcher<? super String> value;

        @SuppressWarnings("unchecked")
        public ParamMatcher(String name, Matcher<? super String> value, boolean nullable) {
            super(name, nullable ? anyOf(nullValue(), hasItem(value)) : anyOf(hasItem(value)));
            this.value = nullable ? anyOf(nullValue(), value) : value;
        }

        public static ParamMatcher urlParam(String name, String value) {
            return urlParam(name, equalTo(value));
        }

        public static ParamMatcher urlParam(String name, Matcher<? super String> matcher) {
            return new ParamMatcher(name, matcher, false);
        }

        public static ParamMatcher urlParamOrNull(String name, String value) {
            return urlParamOrNull(name, equalTo(value));
        }

        public static ParamMatcher urlParamOrNull(String name, Matcher<? super String> matcher) {
            return new ParamMatcher(name, matcher, true);
        }

        @Override
        public void describeTo(Description description) {
            value.describeTo(description.appendText("param \"" + name + "\": "));
        }

        @Override
        protected void describeMismatchSafely(Iterable<? super String> item, Description mismatchDescription) {
            value.describeMismatch(String.valueOf(item), mismatchDescription.appendText("param \"" + name + "\" "));
        }
    }
}
