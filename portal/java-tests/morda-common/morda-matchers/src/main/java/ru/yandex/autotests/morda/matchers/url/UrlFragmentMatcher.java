package ru.yandex.autotests.morda.matchers.url;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.net.URI;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public class UrlFragmentMatcher extends TypeSafeMatcher<String> {

    private Matcher<String> fragmentMatcher;
    private String fragment;

    public UrlFragmentMatcher(String fragment) {
        this(equalTo(fragment));
    }

    public UrlFragmentMatcher(Matcher<String> fragmentMatcher) {
        this.fragmentMatcher = fragmentMatcher;
    }

    public static UrlFragmentMatcher fragment(String fragment) {
        return new UrlFragmentMatcher(fragment);
    }

    public static UrlFragmentMatcher fragment(Matcher<String> fragmentMatcher) {
        return new UrlFragmentMatcher(fragmentMatcher);
    }

    @Override
    protected boolean matchesSafely(String item) {
        fragment = URI.create(item).getFragment();
        return fragmentMatcher.matches(fragment);
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("anchor ")
                .appendDescriptionOf(fragmentMatcher);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        mismatchDescription.appendText("anchor was \"")
                .appendText(fragment)
                .appendText("\"");
    }
}
