package ru.yandex.taxi.conversation.utils;

import java.util.List;
import java.util.stream.Stream;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.test.context.TestPropertySource;

import ru.yandex.mj.generated.client.telephony.model.AppendCallScriptRequest;
import ru.yandex.mj.generated.server.model.CallNotice;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.util.ResourceHelpers;
import ru.yandex.taxi.conversation.utils.logging.TelephonyLogUtils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration.JSON_OBJECT_MAPPER;

@TestPropertySource(locations = "classpath:/chat/angry/data_test.properties")
class TelephonyLogUtilsTest extends AbstractFunctionalTest {

    @Autowired
    @Qualifier(JSON_OBJECT_MAPPER)
    private ObjectMapper objectMapper;

    private static Stream<Arguments> receivedToLogExamples() {
        return Stream.of(
                arguments(
                        "without actions",
                        "/telephony/callnotice/example_without_actions.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Call notice received. " +
                                "abonentNumber:+79220000001"
                ),
                arguments(
                        "with forward action",
                        "/telephony/callnotice/example_with_forward_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Call notice received. " +
                                "abonentNumber:+79220000001 FORWARD:status:processing"
                ),
                arguments(
                        "with answer action",
                        "/telephony/callnotice/example_with_answer_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Call notice received. " +
                                "abonentNumber:+79220000001 ANSWER:status:completed"
                ),
                arguments(
                        "with hold action",
                        "/telephony/callnotice/example_with_hold_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Call notice received. " +
                                "abonentNumber:+79220000001 HOLD:status:completed"
                ),
                arguments(
                        "with hangup action",
                        "/telephony/callnotice/example_with_hangup_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Call notice received. " +
                                "abonentNumber:+79220000001 HANGUP:cause:normal-clearing"
                )
        );
    }

    private static Stream<Arguments> receiverSentToLogExamples() {
        return Stream.of(
                arguments(
                        "without actions",
                        "/telephony/callnotice/example_without_actions.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Receiver sent. " +
                                "abonentNumber:+79220000001"
                ),
                arguments(
                        "with forward action",
                        "/telephony/callnotice/example_with_forward_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Receiver sent. " +
                                "abonentNumber:+79220000001 ANSWER:status:completed HOLD:status:completed FORWARD:status:processing HANGUP:cause:normal-clearing"
                ),
                arguments(
                        "with answer action",
                        "/telephony/callnotice/example_with_answer_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Receiver sent. " +
                                "abonentNumber:+79220000001 ANSWER:status:completed HOLD:status:completed FORWARD:status:processing HANGUP:cause:normal-clearing"
                ),
                arguments(
                        "with hold action",
                        "/telephony/callnotice/example_with_hold_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Receiver sent. " +
                                "abonentNumber:+79220000001 ANSWER:status:completed HOLD:status:completed FORWARD:status:processing HANGUP:cause:normal-clearing"
                ),
                arguments(
                        "with hangup action",
                        "/telephony/callnotice/example_with_hangup_action.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Receiver sent. " +
                                "abonentNumber:+79220000001 ANSWER:status:completed HOLD:status:completed FORWARD:status:processing HANGUP:cause:normal-clearing"
                )
        );
    }

    private static Stream<Arguments> dispatchToLogTestExamples() {
        return Stream.of(
                arguments(
                        "script_forward",
                        "/telephony/appendcallscriptrequest/example_script_forward.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Send actions script. " +
                                "FORWARD:yandexUid:1120000000313156:timeoutSec:10"
                ),
                arguments(
                        "script_hangup",
                        "/telephony/appendcallscriptrequest/example_script_hangup.json",
                        "History callExternalId:0000061102-7135185458-1646046623-0029194569. Send actions script. " +
                                "HANGUP:cause:normal-clearing"
                )
        );
    }

    @MethodSource("receivedToLogExamples")
    @ParameterizedTest(name = "{0}")
    public void receivedToLogTest(String description,
                                  String jsonPath,
                                  String expected
    ) throws Exception {
        // arrange
        byte[] exampleJson = ResourceHelpers.getResource(jsonPath);
        CallNotice example = objectMapper.readValue(exampleJson, CallNotice.class);

        // act
        var result = TelephonyLogUtils.receivedToLog(example);

        // assert
        assertEquals(expected, result);
    }

    @MethodSource("dispatchToLogTestExamples")
    @ParameterizedTest(name = "{0}")
    public void dispatchToLogTest(String description,
                                  String jsonPath,
                                  String expected
    ) throws Exception {
        // arrange
        byte[] exampleJson = ResourceHelpers.getResource(jsonPath);
        AppendCallScriptRequest example = objectMapper.readValue(exampleJson, AppendCallScriptRequest.class);

        // act
        var result = TelephonyLogUtils.dispatchToLog(
                "0000061102-7135185458-1646046623-0029194569",
                example.getActions());

        // assert
        assertEquals(expected, result);
    }

    @MethodSource("receiverSentToLogExamples")
    @ParameterizedTest(name = "{0}")
    public void receiverSentToLogTest(String description,
                                      String jsonPath,
                                      String expected
    ) throws Exception {
        // arrange
        byte[] exampleJson = ResourceHelpers.getResource(jsonPath);
        TestActionHolder example = objectMapper.readValue(exampleJson, TestActionHolder.class);

        // act
        var result = TelephonyLogUtils.receiverSentToLog(
                "0000061102-7135185458-1646046623-0029194569",
                "+79220000001",
                example.getActions());

        // assert
        assertEquals(expected, result);
    }

    public static class TestActionHolder {

        @JsonProperty("actions")
        private List<ru.yandex.mj.generated.server.model.CallAction> actions;

        @JsonCreator
        public TestActionHolder(@JsonProperty("actions") List<ru.yandex.mj.generated.server.model.CallAction> actions) {
            this.actions = actions;
        }

        public List<ru.yandex.mj.generated.server.model.CallAction> getActions() {
            return actions;
        }

        public void setActions(List<ru.yandex.mj.generated.server.model.CallAction> actions) {
            this.actions = actions;
        }
    }
}
