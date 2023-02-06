package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Matcher;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentSource;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;

/**
 * Created by sonick on 15.09.16.
 */
public class SegmentMatchers {

    public static Matcher<Segment> segmentSourceEqualTo(SegmentSource segmentSource) {
        return having(on(Segment.class).getSegmentSource(), equalTo(segmentSource));
    }
}
