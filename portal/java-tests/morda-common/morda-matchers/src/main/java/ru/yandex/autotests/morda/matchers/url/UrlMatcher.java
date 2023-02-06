package ru.yandex.autotests.morda.matchers.url;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;
import static ru.yandex.autotests.morda.matchers.url.UrlQueryMatcher.queryMatcher;

/**
 * User: asamar
 * Date: 07.08.2015.
 */
public class UrlMatcher extends TypeSafeMatcher<String> {

    private List<Matcher<String>> failedMatchers;
    private UrlSchemeMatcher schemeMatcher;
    private UrlHostMatcher hostMatcher;
    private UrlPathMatcher pathMatcher;
    private UrlQueryMatcher queryMatcher;
    private UrlFragmentMatcher fragmentMatcher;
    private boolean strict;

    public UrlMatcher() {
        this(false);
    }

    public UrlMatcher(boolean strict) {
        this.strict = strict;
        this.queryMatcher = queryMatcher();
    }

    public static UrlMatcher urlMatcher() {
        return new UrlMatcher();
    }

    public static UrlMatcher urlMatcher(boolean strict) {
        return new UrlMatcher(strict);
    }

    public static UrlMatcher urlMatcher(URI uri, boolean strict) {
        return new UrlMatcher(strict)
                .scheme(uri.getScheme())
                .host(uri.getHost())
                .path(uri.getPath())
                .fragment(uri.getFragment())
                .query(queryMatcher(uri.getRawQuery()));
    }

    public static UrlMatcher urlMatcher(URI uri) {
        return urlMatcher(uri, false);
    }

    public static UrlMatcher urlMatcher(String uri) {
        return urlMatcher(URI.create(uri), false);
    }

    public static UrlMatcher urlMatcher(String uri, boolean strict) {
        return urlMatcher(URI.create(uri), strict);
    }

    public UrlHostMatcher getHostMatcher() {
        return hostMatcher;
    }

    public UrlPathMatcher getPathMatcher() {
        return pathMatcher;
    }

    public UrlQueryMatcher getQueryMatcher() {
        return queryMatcher;
    }

    public UrlSchemeMatcher getSchemeMatcher() {
        return schemeMatcher;
    }

    public UrlMatcher scheme(String scheme) {
        this.schemeMatcher = UrlSchemeMatcher.scheme(scheme);
        return this;
    }

    public UrlMatcher scheme(Matcher<String> schemeMatcher) {
        this.schemeMatcher = UrlSchemeMatcher.scheme(schemeMatcher);
        return this;
    }

    public UrlMatcher scheme(UrlSchemeMatcher schemeMatcher) {
        this.schemeMatcher = schemeMatcher;
        return this;
    }

    public UrlMatcher host(String host) {
        this.hostMatcher = UrlHostMatcher.host(host);
        return this;
    }

    public UrlMatcher host(Matcher<String> hostMatcher) {
        this.hostMatcher = UrlHostMatcher.host(hostMatcher);
        return this;
    }

    public UrlMatcher host(UrlHostMatcher hostMatcher) {
        this.hostMatcher = hostMatcher;
        return this;
    }

    public UrlMatcher path(String path) {
        this.pathMatcher = UrlPathMatcher.path(path);
        return this;
    }

    public UrlMatcher path(Matcher<String> pathMatcher) {
        this.pathMatcher = UrlPathMatcher.path(pathMatcher);
        return this;
    }

    public UrlMatcher path(UrlPathMatcher pathMatcher) {
        this.pathMatcher = pathMatcher;
        return this;
    }

    public UrlMatcher fragment(String fragment) {
        this.fragmentMatcher = UrlFragmentMatcher.fragment(fragment);
        return this;
    }

    public UrlMatcher fragment(Matcher<String> pathMatcher) {
        this.fragmentMatcher = UrlFragmentMatcher.fragment(pathMatcher);
        return this;
    }

    public UrlMatcher fragment(UrlFragmentMatcher fragmentMatcher) {
        this.fragmentMatcher = fragmentMatcher;
        return this;
    }

    public UrlMatcher query(UrlQueryMatcher queryMatcher) {
        this.queryMatcher = queryMatcher;
        return this;
    }

    public UrlMatcher query(String query) {
        this.queryMatcher = queryMatcher(query);
        return this;
    }

    public UrlMatcher query(String key, String value) {
        this.queryMatcher.param(key, value);
        return this;
    }

    public UrlMatcher query(String key, Matcher<? super String> value) {
        this.queryMatcher.param(key, value);
        return this;
    }

    @Override
    public void describeTo(Description description) {
        String d = getAllMatchers().stream()
                .filter(e -> e != null)
                .map(Object::toString)
                .collect(joining(", "));
        description.appendText(d);
    }

    private List<Matcher<String>> getAllMatchers() {
        return asList(schemeMatcher, hostMatcher, pathMatcher, fragmentMatcher, queryMatcher);
    }

    @Override
    protected boolean matchesSafely(String s) {
        failedMatchers = getAllMatchers().stream()
                .filter(e -> e != null && !e.matches(s))
                .collect(Collectors.toList());
        return failedMatchers.isEmpty();
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        failedMatchers.stream()
                .filter(e -> e != null)
                .forEach(e -> {
                    e.describeMismatch(item, mismatchDescription);
                    mismatchDescription.appendText(", ");
                });
    }
}
