package ru.yandex.autotests.morda.matchers.har;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.morda.matchers.url.UrlMatcher;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static net.lightbody.bmp.core.util.ThreadUtils.sleep;

public class HarRequestMatcher extends TypeSafeMatcher<Har> {

    private List<HarEntry> entries;
    private Predicate<HarEntry> requestFilter;
    private UrlMatcher urlMatcher;

    public HarRequestMatcher(Predicate<HarEntry> requestFilter, UrlMatcher urlMatcher) {
        this.requestFilter = requestFilter;
        this.urlMatcher = urlMatcher;
    }

    @Factory
    public static HarRequestMatcher request(Predicate<HarEntry> requestFilter, UrlMatcher urlMatcher) {
        return new HarRequestMatcher(requestFilter, urlMatcher);
    }

    @Override
    protected boolean matchesSafely(Har har) {
        sleep(TimeUnit.MILLISECONDS, 1000);

        entries = har.getLog().getEntries().stream().filter(requestFilter)
                .collect(Collectors.toList());

        return entries.size() == 1 && urlMatcher.matches(entries.get(0).getRequest().getUrl());
    }

    @Override
    public void describeTo(Description description) {
        urlMatcher.describeTo(description.appendText("Request"));
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        if (entries.size() == 0) {
            mismatchDescription.appendText("No request found");
        } else if (entries.size() > 1) {
            mismatchDescription.appendText("More than 1 request found");
        } else {
            urlMatcher.describeMismatch(entries.get(0).getRequest().getUrl(), mismatchDescription);
        }
    }
}
