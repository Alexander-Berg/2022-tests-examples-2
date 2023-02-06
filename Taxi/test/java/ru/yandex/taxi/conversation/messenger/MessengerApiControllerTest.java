package ru.yandex.taxi.conversation.messenger;

import java.util.List;
import java.util.stream.Stream;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.util.ResourceHelpers;

import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:/messenger/messenger_test.properties")
public class MessengerApiControllerTest  extends AbstractFunctionalTest {

    @Autowired
    private MockMvc mockMvc;

    private static Stream<Arguments> deliveryReports() {
        return Stream.of(
                arguments(
                        "whatsapp delivery report: valid",
                        "/messenger/whatsapp/deliveryReportMessage.json",
                        MessengerEvent.deliveryReportMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "telegram delivery report: valid",
                        "/messenger/telegram/deliveryReportMessage.json",
                        MessengerEvent.deliveryReportMessage(),
                        List.of(status().isOk())
                )
        );
    }

    private static Stream<Arguments> whatsappInboundMessages() {
        return Stream.of(
                arguments(
                        "inbound whatsapp text message: valid",
                        "/messenger/whatsapp/textMessage.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "inbound whatsapp media message: valid",
                        "/messenger/whatsapp/mediaMessage.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "inbound whatsapp voice media message with s3: valid",
                        "/messenger/whatsapp/mediaMessage_voice_with_s3.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                )
        );
    }

    private static Stream<Arguments> telegramInboundMessages() {
        return Stream.of(
                arguments(
                        "inbound telegram text message: valid",
                        "/messenger/telegram/textMessage.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "inbound telegram media message: valid",
                        "/messenger/telegram/mediaMessage.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "inbound telegram media message with s3: valid",
                        "/messenger/telegram/mediaMessage_with_s3.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "inbound telegram voice media message with s3: valid",
                        "/messenger/telegram/mediaMessage_voice_with_s3.json",
                        MessengerEvent.inboundTextMessage(),
                        List.of(status().isOk())
                )
        );
    }

    @MethodSource("whatsappInboundMessages")
    @ParameterizedTest(name = "{0}")
    public void testWhatsappInboundReceiveMessage(String description,
                                 String jsonPath,
                                 MessengerEvent event,
                                 List<ResultMatcher> expectedResult) throws Exception {
        byte[] content = ResourceHelpers.getResource(jsonPath);
        ResultActions resultActions = mockMvc.perform(
                        post("/v1/messenger/message")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(new String(content))
                )
                .andDo(print());
        for (ResultMatcher matcher : expectedResult) {
            resultActions.andExpect(matcher);
        }
    }

    @MethodSource("telegramInboundMessages")
    @ParameterizedTest(name = "{0}")
    public void testTelegramInboundReceiveMessage(String description,
                                                  String jsonPath,
                                                  MessengerEvent event,
                                                  List<ResultMatcher> expectedResult) throws Exception {
        byte[] content = ResourceHelpers.getResource(jsonPath);
        ResultActions resultActions = mockMvc.perform(
                        post("/v1/messenger/message")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(new String(content))
                )
                .andDo(print());
        for (ResultMatcher matcher : expectedResult) {
            resultActions.andExpect(matcher);
        }
    }

    @MethodSource("deliveryReports")
    @ParameterizedTest(name = "{0}")
    public void testinboundDeliveryReport(String description,
                                          String jsonPath,
                                          MessengerEvent event,
                                          List<ResultMatcher> expectedResult) throws Exception {
        byte[] content = ResourceHelpers.getResource(jsonPath);
        ResultActions resultActions = mockMvc.perform(
                        post("/v1/messenger/delivery")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(new String(content))
                )
                .andDo(print());
        for (ResultMatcher matcher : expectedResult) {
            resultActions.andExpect(matcher);
        }
    }
}
