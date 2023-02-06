package ru.yandex.autotests.morda.utils.matchers;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;

import static java.util.stream.Collectors.toList;
import static net.lightbody.bmp.core.util.ThreadUtils.sleep;

public class HarNoRequestMatcher extends TypeSafeMatcher<Har> {

    private List<HarEntry> entries;
    private Predicate<HarEntry> requestFilter;

    public HarNoRequestMatcher(Predicate<HarEntry> requestFilter) {
        this.requestFilter = requestFilter;
    }

    @Factory
    public static HarNoRequestMatcher noRequest(Predicate<HarEntry> requestFilter) {
        return new HarNoRequestMatcher(requestFilter);
    }

    @Override
    protected boolean matchesSafely(Har har) {
        sleep(TimeUnit.MILLISECONDS, 1000);

        entries = har.getLog().getEntries().stream().filter(requestFilter)
                .collect(toList());

        return entries.isEmpty();
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("No request");
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        mismatchDescription.appendText("Some requests found: " + entries.stream()
                        .map(e -> e.getRequest().getUrl())
                        .collect(toList())
        );
    }
}
