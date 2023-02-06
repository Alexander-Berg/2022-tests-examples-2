package ru.yandex.autotests.morda.utils.matchers;

import net.lightbody.bmp.core.har.Har;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class StaticDownloadedMatcher extends TypeSafeMatcher<Har> {
    private List<String> errors = new ArrayList<String>();

    @Factory
    public static StaticDownloadedMatcher staticDownloaded() {
        return new StaticDownloadedMatcher();
    }

    @Override
    protected boolean matchesSafely(Har har) {
        errors.addAll(har.getLog().getEntries().stream()
                .filter(
                        e -> e.getResponse().getStatus() >= 400
                )
                .map(e -> e.getResponse().getStatus() + ": " + e.getRequest().getUrl())
                .collect(Collectors.toList()));
        return errors.size() == 0;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("All requests return code < 400");
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        for (String error : errors) {
            mismatchDescription.appendText("[").appendText(error).appendText("]\n");
        }
    }
}
