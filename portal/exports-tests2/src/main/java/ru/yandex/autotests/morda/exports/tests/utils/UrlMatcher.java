package ru.yandex.autotests.morda.exports.tests.utils;

import org.apache.http.NameValuePair;
import org.apache.http.client.utils.URLEncodedUtils;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.hamcrest.StringDescription;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * User: asamar
 * Date: 07.08.2015.
 */
public class UrlMatcher extends TypeSafeMatcher<String> {

    private Matcher<String> scheme;
    private Matcher<String> host;
    private Matcher<String> path;
    private List<ParamMatcher> params;
    private Description describeMismatch;
    private Description description;

    public void setParams(ParamMatcher... params) {
        this.params.addAll(Arrays.asList(params));
    }

    private UrlMatcher(Builder builder) {
        scheme = builder.scheme;
        path = builder.path;
        host = builder.host;
        params = builder.params;
        describeMismatch = new StringDescription().appendText("\n");
        description = new StringDescription().appendText("\n");
    }

    public static class Builder {
        private Matcher<String> scheme;
        private Matcher<String> host;
        private Matcher<String> path;
        private List<ParamMatcher> params;


        public Builder() {
            this.params = new ArrayList<>();
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

        public Builder scheme(Matcher<String> scheme) {
            this.scheme = scheme;
            return this;
        }

        public Builder host(Matcher<String> host) {
            this.host = host;
            return this;
        }

        public Builder path(Matcher<String> path) {
            this.path = path;
            return this;
        }


        public Builder urlParams(List<ParamMatcher> params) {
            this.params.addAll(params);
            return this;
        }

        public Builder urlParams(ParamMatcher... params){
            return urlParams(Arrays.asList(params));
        }

        public UrlMatcher build() {
            return new UrlMatcher(this);
        }
    }

    public static UrlMatcher.Builder urlMatcher(){
        return new UrlMatcher.Builder();
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("\n");
        describe(scheme, description.appendText("sheme: "));
        describe(host, description.appendText("host: "));
        describe(path, description.appendText("path: "));
        params.forEach(pm ->
                describe(pm.getMatcher(), description.appendText("param \"" + pm.getName() + "\": ")));
    }

    @Override
    protected boolean matchesSafely(String s) {

        final URI uri = URI.create(s.replace("|", "%7C"));
        /*Map<String, String> map = URLEncodedUtils.parse(uri, "UTF-8").stream()
                .collect(Collectors.toMap(NameValuePair::getName, NameValuePair::getValue));*/

        Map<String, String> map = new HashMap<>();
        for(NameValuePair nm: URLEncodedUtils.parse(s, Charset.forName("UTF-8"), '&', '?')) {
            map.put(nm.getName(), nm.getValue());
        }

        return isMatches(scheme, uri.getScheme(), "scheme ") &&
                isMatches(host, uri.getHost(), "host ") &&
                isMatches(path, uri.getPath(), "path ") &&
                params.stream()
                        .allMatch(pm ->
                                isMatches(pm.getMatcher(), map.get(pm.getName()), "param \"" + pm.getName() + "\" "));
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText(this.describeMismatch.toString());
    }

    private boolean isMatches(Matcher<String> matcher, String obj, String name) {
        if (matcher != null && !matcher.matches(obj)) {
            matcher.describeMismatch(obj, describeMismatch.appendText(name));
            describeMismatch.appendText("\n");
            return false;
        }
        return true;
    }

    private void describe(Matcher<String> matcher, Description description) {
        if (matcher != null) {
            matcher.describeTo(description);
            description.appendText("\n");
        }
    }

    public static class ParamMatcher<T> {

        private String name;
        private Matcher<String> matcher;

        /*public ParamMatcher(String name, String value) {
            new ParamMatcher(name, Matchers.equalToIgnoringCase(value));
        }*/

        public static ParamMatcher urlParam(String name, String value){
            return urlParam(name, Matchers.equalTo(value));
        }

        public static ParamMatcher urlParam(String name, Matcher<String> matcher){
            return new ParamMatcher(name, matcher);
        }

/*        public static <T>  ParamMatcher urlParam(String name, Function<T, String> eq){
            return new ParamMatcher(name, "");
        }*/

        public ParamMatcher(String name, Matcher<String> value) {
            this.name = name;
            this.matcher = value;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public void setMatcher(Matcher<String> matcher) {
            this.matcher = matcher;
        }

        public Matcher<String> getMatcher() {
            return matcher;
        }

    }


}
