package ru.yandex.autotests.metrika.matchers.inpage;

import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.matchers.ReportDataMatcher;

public class InpageNotEmptyMatchers {

    private InpageNotEmptyMatchers() {
    }

    public static Matcher getNotEmptyInpageMatcher(Object item) {
        if (item instanceof MapsV1DataLinkMapGETSchema) {
            return LinkMapMatcher.expectNotEmpty();
        } else if (item instanceof MapsV1DataClickGETSchema) {
            return ClickMapMatcher.expectNotEmpty();
        } else if (item instanceof MapsV1DataFormGETPOSTSchema) {
            return FormMapMatcher.expectNotEmpty();
        } else if (item instanceof MapsV1DataScrollGETSchema) {
            return ReportDataMatcher.expectNotEmptyReport();
        } else {
            throw new IllegalArgumentException("unsupported response type:" + item.getClass().getCanonicalName());
        }
    }
}
