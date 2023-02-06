package ru.yandex.metrika.mobmet.crash.decoder.test.daemon;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;

import org.hamcrest.Description;
import org.hamcrest.DiagnosingMatcher;
import org.hamcrest.Matcher;
import org.skyscreamer.jsonassert.JSONCompare;
import org.skyscreamer.jsonassert.JSONCompareMode;
import org.skyscreamer.jsonassert.JSONCompareResult;

import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashProcessingFields;
import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashTestData;
import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashTestDataReader;
import ru.yandex.metrika.mobmet.crash.decoder.steps.MobileEvent;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang.StringUtils.isEmpty;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.irt.testutils.beans.BeanHelper.copyProperties;
import static ru.yandex.metrika.mobmet.crash.decoder.steps.MobmetCrashDecoderSteps.sortChunk;

public class Matchers {

    public static Matcher<List<MobileEvent>> equalToMobileEvents(List<MobileEvent> expectedParams, Function<List<MobileEvent>, List<MobileEvent>> transformer) {
        expectedParams = transformer.apply(expectedParams);
        return equalToMobileEvents(expectedParams);
    }

    public static Matcher<List<MobileEvent>> equalToMobileEvents(List<MobileEvent> expectedParams) {
        return new CrashChunkMatcher(expectedParams);
    }

    public static class CrashChunkMatcher extends DiagnosingMatcher<List<MobileEvent>> {

        private final List<MobileEvent> expectedChunk;

        public CrashChunkMatcher(List<MobileEvent> expectedChunk) {
            this.expectedChunk = expectedChunk;
        }

        @Override
        protected boolean matches(Object actual, Description mismatchDescription) {
            if (!isNotNull(actual, mismatchDescription)) {
                return false;
            }
            List<MobileEvent> actualChunk = (List<MobileEvent>) actual;
            if (expectedChunk.size() != actualChunk.size()) {
                mismatchDescription.appendText(
                        "Expected chunk of size " + expectedChunk.size() + " but was " + actualChunk.size());
                return false;
            }
            for (int i = 0; i < actualChunk.size(); ++i) {
                MobileEvent actualEvent = actualChunk.get(i);
                MobileEvent expectedEvent = expectedChunk.get(i);

                // Сравниваем поля событий, кроме некоторых
                Matcher<MobileEvent> fieldsMatcher = beanEquivalent(expectedEvent)
                        .fields(ignore("decodeTimestamp", "crashDecodedEventValue"));
                if (!fieldsMatcher.matches(actualEvent)) {
                    fieldsMatcher.describeMismatch(actualEvent, mismatchDescription);
                    return false;
                }

                // Сравниваем результат декодирования с ожидаемым
                String expectedEventValue = expectedEvent.getCrashDecodedEventValue();
                String actualEventValue = actualEvent.getCrashDecodedEventValue();
                if (isEmpty(actualEventValue) && isEmpty(expectedEventValue) ||
                        Objects.equals(actualEventValue, expectedEventValue)) {
                    continue;
                }
                if (isEmpty(actualEventValue) && !isEmpty(expectedEventValue)) {
                    mismatchDescription.appendText(
                            "[" + i + "] Decoded event value expected to be non-empty but was '" + actualEventValue + "'");
                    return false;
                }
                if (!isEmpty(actualEventValue) && isEmpty(expectedEventValue)) {
                    mismatchDescription.appendText(
                            "[" + i + "] Decoded event value expected to be empty but was '" + actualEventValue + "'");
                    return false;
                }
                JSONCompareResult jsonCompareResult =
                        JSONCompare.compareJSON(expectedEventValue, actualEventValue, JSONCompareMode.STRICT);
                if (jsonCompareResult.failed()) {
                    mismatchDescription.appendText("" +
                            "[" + i + "] Decoded event value doesn't match the expected value. Json diff:\n" +
                            jsonCompareResult.getMessage());
                    return false;
                }
            }
            return true;
        }

        @Override
        public void describeTo(Description description) {
            // Пишется в Expected:
            description.appendText("CrashChunkMatcher to return 'true'");
        }
    }

    public static List<MobileEvent> withIODecodeParams(List<MobileEvent> mobileEvents) {
        return mobileEvents.stream()
                .peek(event -> event.withDecodeStatus("unknown").withDecodeErrorDetails("Unsupported OS windows"))
                .collect(toList());
    }

    public static List<MobileEvent> withInvalidatedEventsDecodeParams(List<MobileEvent> mobileEvents) {
        return mobileEvents.stream()
                .peek(event -> event.withDecodeStatus("parse_error").withDecodeErrorDetails("Invalidated event"))
                .collect(toList());
    }

    public static List<MobileEvent> withRateLimitedEventsParams(List<MobileEvent> mobileEvents) {
        return mobileEvents.stream()
                .peek(event -> {
                    if (event.getEventNumber().longValue() >= 100) {
                        event.setInvalidationReasons(new String[]{"Rate limited by crash-decoder"});
                    } else {
                        event.setDecodeStatus("parse_error");
                    }
                })
                .collect(toList());
    }

    public static List<MobileEvent> withVersionsDecodeParams(List<MobileEvent> mobileEvents) {
        MobileEvent newCrash = mobileEvents.get(0);
        CrashTestData newCrashData = CrashTestDataReader.readCrashForDecode(newCrash.getEventID().longValue());
        fillCrashFields(newCrash, newCrashData.getExpected().get(0));

        MobileEvent parsedCrash = mobileEvents.get(1);

        MobileEvent decodedCrash = new MobileEvent();
        copyProperties(decodedCrash, parsedCrash);
        CrashTestData decodedCrashData = CrashTestDataReader.readCrashForDecode(decodedCrash.getEventID().longValue());
        fillCrashFields(decodedCrash, decodedCrashData.getExpected().get(0));
        decodedCrash.setVersion(parsedCrash.getVersion().add(BigInteger.ONE));

        parsedCrash.withSign(-1);

        List<MobileEvent> result = new ArrayList<>();
        result.add(newCrash);
        result.add(parsedCrash);
        result.add(decodedCrash);
        return result;
    }

    public static List<MobileEvent> withDecodeParams(MobileEvent mobileEvent, CrashTestData crashTestData) {
        List<MobileEvent> result = new ArrayList<>();
        // При декодировании одного события на выходе может получиться несколько.
        // Например, если крэш случился в библиотеке, в которой используется собственный APIKey, то
        // крэш должен раздвоиться на библиотеку и на приложение.
        for (CrashProcessingFields expectedFields : crashTestData.getExpected()) {
            MobileEvent mobileEventCopy = new MobileEvent(mobileEvent);
            fillCrashFields(mobileEventCopy, expectedFields);
            result.add(mobileEventCopy);
        }
        return sortChunk(result);
    }

    private static void fillCrashFields(MobileEvent event, CrashProcessingFields expectedData) {
        event
                .withAPIKey(expectedData.getApiKey())
                .withEventID(expectedData.getEventID())
                .withCrashEncodeType(expectedData.getCrashEncodeType())
                .withDecodeStatus(expectedData.getDecodeStatus())
                .withDecodeGroupID(expectedData.getDecodeGroupId())
                .withOSBuild(expectedData.getOsBuild())
                .withDecodeRequiredSymbolsId(expectedData.getDecodeRequiredSymbolsId())
                .withDecodeUsedSymbolsIds(expectedData.getDecodeUsedSymbolsIds().toArray(new String[]{}))
                .withDecodeMissedSymbolsIds(expectedData.getDecodeMissedSymbolsIds().toArray(new String[]{}))
                .withDecodeUsedSystemSymbolsIds(expectedData.getDecodeUsedSystemSymbolsIds().toArray(new String[]{}))
                .withDecodeMissedSystemSymbolsIds(expectedData.getDecodeMissedSystemSymbolsIds().toArray(new String[]{}))
                .withCrashReasonType(expectedData.getCrashReasonType())
                .withCrashReason(expectedData.getCrashReason())
                .withCrashReasonMessage(expectedData.getCrashReasonMessage())
                .withCrashBinaryName(expectedData.getCrashBinaryName())
                .withCrashFileName(expectedData.getCrashFileName())
                .withCrashMethodName(expectedData.getCrashMethodName())
                .withCrashSourceLine(BigInteger.valueOf(expectedData.getCrashSourceLine()))
                .withCrashDecodedEventValue(expectedData.getCrashDecodedEventValue())
                .withCrashThreadContent(expectedData.getCrashThreadContent())
                .withDecodeOriginalAPIKey(expectedData.getDecodeOriginalAPIKey())
                .withDecodeOriginalEventID(BigInteger.valueOf((expectedData.getDecodeOriginalEventID())));
    }

}
