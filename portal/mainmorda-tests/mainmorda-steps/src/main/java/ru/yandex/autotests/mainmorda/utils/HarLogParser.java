package ru.yandex.autotests.mainmorda.utils;

import ch.lambdaj.Lambda;
import ch.lambdaj.function.convert.Converter;
import ch.lambdaj.function.matcher.Predicate;
import net.lightbody.bmp.core.har.HarEntry;
import net.lightbody.bmp.core.har.HarLog;
import net.lightbody.bmp.core.har.HarNameValuePair;
import org.hamcrest.Matcher;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 04.12.2014.
 */
public class HarLogParser {
    private final HarLog harLog;

    public HarLogParser(HarLog harLog) {
        this.harLog = harLog;
    }

    public List<Map<String,String>> getSuggestsParameters() {
        List<HarEntry> filteredEntries = Lambda.filter(suggestEntryMatcher, harLog.getEntries());
        return Lambda.convert(Lambda.extract(filteredEntries, Lambda.on(HarEntry.class).getRequest().getQueryString()), new QueryStringConverter());
    }

    private class QueryStringConverter implements Converter<List<HarNameValuePair>, Map<String, String>> {
        @Override
        public Map<String, String> convert(List<HarNameValuePair> harNameValuePairs) {
            Map<String, String> map = new HashMap<>();
            for (HarNameValuePair pair: harNameValuePairs) {
                map.put(pair.getName(), pair.getValue());
            }
            return map;
        }
    }

    private Matcher<HarEntry> suggestEntryMatcher = new Predicate<HarEntry>() {
        @Override
        public boolean apply(HarEntry harEntry) {
            return harEntry.getRequest().getUrl().contains("suggest");
        }
    };
}
