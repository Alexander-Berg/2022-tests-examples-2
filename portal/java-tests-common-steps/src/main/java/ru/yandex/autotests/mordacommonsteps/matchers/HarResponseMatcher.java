package ru.yandex.autotests.mordacommonsteps.matchers;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.lessThan;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04.07.13
 */
public class HarResponseMatcher extends TypeSafeMatcher<Har> {
    private Matcher<Integer> matcher;
    private Predicate<HarEntry> harEntryPredicate;
    private List<String> errors = new ArrayList<String>();

    public HarResponseMatcher() {
        this(lessThan(400));
    }

    public HarResponseMatcher(Matcher<Integer> matcher) {
        this(matcher, (harEntry) -> true);
    }

    public HarResponseMatcher(Predicate<HarEntry> harEntryPredicate) {
        this(lessThan(400), harEntryPredicate);
    }

    public HarResponseMatcher(Matcher<Integer> matcher, Predicate<HarEntry> harEntryPredicate) {
        this.matcher = matcher;
        this.harEntryPredicate = harEntryPredicate;
    }

    @Override
    protected boolean matchesSafely(Har har) {
        List<HarEntry> entries = har.getLog().getEntries().stream()
                .filter(harEntryPredicate)
                .collect(toList());

        for (HarEntry e : entries) {
            System.out.println(e.getRequest().getUrl());
            if (!matcher.matches(e.getResponse().getStatus())) {
                errors.add(e.getResponse().getStatus() + ": " + e.getRequest().getUrl());
            }
        }
        return errors.isEmpty();
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("All requests return code that is " + matcher);
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        for (String error : errors) {
            mismatchDescription.appendText("[").appendText(error).appendText("]\n");
        }
    }

    @Factory
    public static HarResponseMatcher harResponses() {
        return new HarResponseMatcher();
    }

    @Factory
    public static HarResponseMatcher harResponses(Matcher<Integer> matcher) {
        return new HarResponseMatcher(matcher);
    }

    @Factory
    public static HarResponseMatcher harResponses(Predicate<HarEntry> harEntryPredicate){
        return new HarResponseMatcher(harEntryPredicate);
    }

    @Factory
    public static HarResponseMatcher harResponses(Matcher<Integer> matcher, Predicate<HarEntry> harEntryPredicate){
        return new HarResponseMatcher(matcher, harEntryPredicate);
    }
}
