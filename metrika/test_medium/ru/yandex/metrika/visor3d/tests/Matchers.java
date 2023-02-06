package ru.yandex.metrika.visor3d.tests;

import java.util.Comparator;
import java.util.List;
import java.util.Map;

import com.google.protobuf.InvalidProtocolBufferException;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.visor3d.steps.EventPacket;
import ru.yandex.metrika.visor3d.steps.ScrollPacket;
import ru.yandex.metrika.visor3d.steps.Visor3dOutput;
import ru.yandex.metrika.visor3d.steps.WebVisor2;
import ru.yandex.metrika.visor3d.steps.WebVisorLog;
import ru.yandex.metrika.wv2.proto.Events;
import ru.yandex.metrika.wv2.proto.LogbrokerMessages.LogbrokerMessage;
import ru.yandex.metrika.wv2.proto.LogbrokerMessages.LogbrokerMessage.DataType;
import ru.yandex.metrika.wv2.proto.Pages;
import ru.yandex.metrika.wv2.proto.RecorderProto;

import static java.util.Comparator.comparing;
import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasProperty;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.metrika.common.test.medium.OrderedListDiffer.orderedListCompareStrategy;
import static ru.yandex.metrika.visor3d.steps.Visor3dGenerationSteps.eventPacketsFromWebVisorLogs;
import static ru.yandex.metrika.visor3d.steps.Visor3dGenerationSteps.scrollPacketsFromWebVisorLogs;
import static ru.yandex.metrika.visor3d.steps.Visor3dGenerationSteps.webVisor2FromWebVisorLogs;
import static ru.yandex.metrika.wv2.proto.RecorderProto.Wrapper.DataCase.EVENT;
import static ru.yandex.metrika.wv2.proto.RecorderProto.Wrapper.DataCase.PAGE;

public class Matchers {

    protected static final Logger log = LoggerFactory.getLogger(Matchers.class);

    public static Matcher<Visor3dOutput> tablesNotExist() {
        return allOf(
                hasProperty("eventsTableEmpty", equalTo(true))
        );
    }

    public static Matcher<Visor3dOutput> matchWebVisorLogs(List<WebVisorLog> chunk) {
        return allOf(
                hasProperty("events", matchEventPacketsFromWebVisorLogs(chunk)),
                hasProperty("webVisorEvents", matchWebVisor2FromWebVisorLogs(chunk)),
                hasProperty("scrolls", matchScrollPacketsFromWebVisorLogs(chunk))
        );
    }

    public static Matcher<Visor3dOutput> matchWebVisorLogsWithMessages(List<WebVisorLog> chunk) {
        return allOf(
                matchWebVisorLogs(chunk),
                hasProperty("logbrokerMessages", matchLogbrokerMessagesFromWebVisorLogs(chunk))
        );
    }

    public static Matcher<Visor3dOutput> matchWebVisorLogsWithoutYT(List<WebVisorLog> chunk) {
        return allOf(
                hasProperty("eventsTableEmpty", equalTo(true)),
                hasProperty("webVisorEvents", matchWebVisor2FromWebVisorLogs(chunk)),
                hasProperty("scrolls", matchScrollPacketsFromWebVisorLogs(chunk))
        );
    }

    public static Matcher<List<EventPacket>> matchEventPacketsFromWebVisorLogs(List<WebVisorLog> chunk) {
        List<EventPacket> expected = eventPacketsFromWebVisorLogs(chunk);
        return beanDiffer(expected).useCompareStrategy(orderedListCompareStrategy(getEventPacketComparator()));
    }

    public static Matcher<List<WebVisor2>> matchWebVisor2FromWebVisorLogs(List<WebVisorLog> chunk) {
        List<WebVisor2> expected = webVisor2FromWebVisorLogs(chunk);
        return beanDiffer(expected).useCompareStrategy(orderedListCompareStrategy(getWebVisor2Comparator()));
    }

    public static Matcher<List<ScrollPacket>> matchScrollPacketsFromWebVisorLogs(List<WebVisorLog> chunk) {
        List<ScrollPacket> expected = scrollPacketsFromWebVisorLogs(chunk);
        return beanDiffer(expected).useCompareStrategy(orderedListCompareStrategy(getScrollPacketComparator()));
    }

    public static Matcher<List<LogbrokerMessage>> matchLogbrokerMessagesFromWebVisorLogs(List<WebVisorLog> chunk) {
        return hasItem((Matcher) anyOf(chunk.stream().map(Matchers::matchLogbrokerMessageFromWebVisorLog).collect(toList())));
    }

    public static Matcher<LogbrokerMessage> matchLogbrokerMessageFromWebVisorLog(WebVisorLog webVisorLog) {
        return allOf(
                hasProperty("counterId", equalTo(webVisorLog.getCounterID().intValue())),
                hasProperty("hit", equalTo((long) webVisorLog.getHit().intValue())),
                hasProperty("userId", equalTo(webVisorLog.getUniqID().longValue())),
                hasData(webVisorLog.getUnserializedData())
        );
    }

    public static Comparator<EventPacket> getEventPacketComparator() {
        return comparing(EventPacket::hashCode);
    }

    public static Comparator<WebVisor2> getWebVisor2Comparator() {
        return comparing(WebVisor2::hashCode);
    }

    public static Comparator<ScrollPacket> getScrollPacketComparator() {
        return comparing(ScrollPacket::hashCode);
    }

    private static Matcher<LogbrokerMessage> hasData(RecorderProto.BufferWrapper expectedData) {
        return new TypeSafeMatcher<LogbrokerMessage>() {
            @Override
            protected boolean matchesSafely(LogbrokerMessage actual) {
                Map<RecorderProto.Wrapper.DataCase, List<RecorderProto.Wrapper>> byDataType = expectedData.getBufferList().stream()
                        .map(RecorderProto.Buffer::getData)
                        .collect(groupingBy(RecorderProto.Wrapper::getDataCase));
                try {
                    if (actual.getType() == DataType.event) {
                        Events.Event event = Events.Event.parser().parseFrom(actual.getData());
                        return byDataType.get(EVENT).stream().anyMatch(f -> f.getEvent().equals(event));
                    } else if (actual.getType() == DataType.page) {
                        Pages.Page page = Pages.Page.parser().parseFrom(actual.getData());
                        return byDataType.get(PAGE).stream().anyMatch(f -> f.getPage().equals(page));
                    }
                } catch (InvalidProtocolBufferException e) {
                    throw new RuntimeException(e);
                }
                throw new IllegalArgumentException("Invalid actual data, unknown type " + actual.getType().name());
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("data should match");
            }
        };
    }

}
