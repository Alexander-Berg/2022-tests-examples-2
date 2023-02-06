package ru.yandex.autotests.morda.matchers.har;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.joining;

public class PageSubrequestsMatcher extends TypeSafeMatcher<Har> {
    private List<HarEntry> errors = new ArrayList<>();

    @Factory
    public static PageSubrequestsMatcher goodSubrequests() {
        return new PageSubrequestsMatcher();
    }

    @Override
    protected boolean matchesSafely(Har har) {
        errors.addAll(har.getLog().getEntries().stream()
                .filter(e -> e.getResponse().getStatus() >= 400)
                .collect(Collectors.toList()));
        return errors.size() == 0;
    }

    public List<HarEntry> getErrors() {
        return errors;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("All requests status code < 400");
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        String error = errors.stream().map(e -> e.getRequest().getUrl() + " >> " + e.getResponse().getStatusText())
                .collect(joining("; "));

        mismatchDescription.appendText("bad requests: ").appendText(error);
    }
}
