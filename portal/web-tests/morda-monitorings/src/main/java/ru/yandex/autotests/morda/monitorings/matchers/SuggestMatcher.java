package ru.yandex.autotests.morda.monitorings.matchers;

import ch.lambdaj.function.convert.Converter;
import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

import java.net.HttpURLConnection;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static ch.lambdaj.Lambda.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/11/14
 */
public class SuggestMatcher extends TypeSafeMatcher<Har> {
    private static final Pattern SUGGEST_URL_PATTERN =
            Pattern.compile("http.+://suggest\\.yandex\\..+/suggest-ya.cgi.+|http.+://(?:www\\.)?yandex.+/suggest(?:-spok)?/suggest-(?:ya.cgi|endings)?.+");

    private List<HarEntry> matchedRequests;
    private List<HarEntry> failedRequests;

    public SuggestMatcher() {
        this.matchedRequests = new ArrayList<>();
        this.failedRequests = new ArrayList<>();
    }

    @Override
    protected boolean matchesSafely(Har har) {
        for (HarEntry harEntry : har.getLog().getEntries()) {
            Matcher m = SUGGEST_URL_PATTERN.matcher(harEntry.getRequest().getUrl());
            if (m.matches()) {
                matchedRequests.add(harEntry);
                if (harEntry.getResponse().getStatus() != HttpURLConnection.HTTP_OK) {
                    failedRequests.add(harEntry);
                }
            }
        }

        return !matchedRequests.isEmpty() && failedRequests.isEmpty();
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Suggest is ok");
    }

    @Override
    protected void describeMismatchSafely(Har item, Description mismatchDescription) {
        mismatchDescription.appendText("Some suggest requests failed: ").appendValue(
                convert(failedRequests, new Converter<HarEntry, String>() {
                    @Override
                    public String convert(HarEntry harEntry) {
                        return harEntry.getResponse().getStatus() + " " + harEntry.getRequest().getUrl();
                    }
                })
        );
    }

    public static SuggestMatcher suggestIsOk() {
        return new SuggestMatcher();
    }
}
