package ru.yandex.taxi.conversation.chat.angry;

import java.util.stream.Stream;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.TestPropertySource;

import ru.yandex.mj.generated.client.angrySpace.api.AngrySpaceApiClient;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.logbroker.read.Message;
import ru.yandex.taxi.conversation.logbroker.read.MessageProcessorService;
import ru.yandex.taxi.conversation.util.LogbrokerMessageHelper;
import ru.yandex.taxi.conversation.util.ResourceHelpers;

import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@TestPropertySource(locations = "classpath:/chat/angry/data_test.properties")
public class OutAngrySpaceFunctionalTest extends AbstractFunctionalTest {

    @Autowired
    private MessageProcessorService messageProcessorService;

    @MockBean
    private AngrySpaceApiClient angrySpaceApiClient;

    private static Stream<Arguments> eventData() {
        return Stream.of(
                arguments(
                        "vk_new_item",
                        ItemOrMessage.item()
                                .setId("61f39b98d1b0b65d09c8ff19")
                                .setText("Ответ оператора (item)"),
                        "/chat/angry/envelope/out_vk_new_item.json"
                ),
                arguments(
                        "vk_new_message",
                        ItemOrMessage.message()
                                .setId("61ff8832d1b0b65d091f9a1b")
                                .setText("Ответ оператора (message)"),
                        "/chat/angry/envelope/out_vk_new_message.json"
                )
        );
    }

    @MethodSource("eventData")
    @ParameterizedTest(name = "{0}")
    public void testSendResponseFromOperator(String description,
                                             ItemOrMessage expected,
                                             String logbrokerEnvelopeJsonPath) {
        byte[] logbrokerData = ResourceHelpers.getResource(logbrokerEnvelopeJsonPath);

        Message message = LogbrokerMessageHelper.createMessage(logbrokerData);
        messageProcessorService.processMessage(message);

        if (expected.isItem) {
            verifySendItem(expected);
        } else {
            verifySendMessage(expected);
        }
    }

    private void verifySendItem(ItemOrMessage item) {
        verify(angrySpaceApiClient, times(1))
                .sendItem(
                        eq(item.getId()),
                        eq("1"),
                        eq(item.getText()),
                        eq(null),
                        eq(null),
                        eq(null),
                        eq(null),
                        eq(null)
                );
    }

    private void verifySendMessage(ItemOrMessage message) {
        verify(angrySpaceApiClient, times(1))
                .sendChatMessage(
                        eq(message.getId()),
                        eq(message.getText()),
                        eq(null),
                        eq(null),
                        eq(null),
                        eq(null),
                        eq(null)
                );
    }

    private static class ItemOrMessage {
        private final boolean isItem;
        private String id;
        private String text;

        private ItemOrMessage(boolean isItem) {
            this.isItem = isItem;
        }

        public static ItemOrMessage item() {
            return new ItemOrMessage(true);
        }

        public static ItemOrMessage message() {
            return new ItemOrMessage(false);
        }

        public boolean isItem() {
            return isItem;
        }

        public String getId() {
            return id;
        }

        public ItemOrMessage setId(String id) {
            this.id = id;
            return this;
        }

        public String getText() {
            return text;
        }

        public ItemOrMessage setText(String text) {
            this.text = text;
            return this;
        }
    }
}
