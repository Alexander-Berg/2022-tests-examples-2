package ru.yandex.taxi.conversation.chat.angry;

import java.util.List;
import java.util.stream.Stream;

import org.junit.jupiter.api.Test;
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
import ru.yandex.taxi.conversation.receive.chat.exception.ChatExceptionHandler;
import ru.yandex.taxi.conversation.util.ResourceHelpers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:/chat/angry/data_test.properties")
public class AngrySpaceApiControllerTest extends AbstractFunctionalTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ChatExceptionHandler chatExceptionHandler;

    private static Stream<Arguments> eventData() {
        return Stream.of(
                arguments(
                        "new item: valid",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.newItem(),
                        List.of(status().isOk())
                ),
                arguments(
                        "new item: unsupported endpoint",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.newItem()
                                .setScreenName("invalid"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: invalid (provider=VK)")
                        )
                ),
                arguments(
                        "new item: unsupported provider",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.newItem()
                                .setProvider("twitter"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: vk_public_test (provider=TWITTER)")
                        )
                ),
                arguments(
                        "edit item: valid",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.editItem(),
                        List.of(status().isOk())
                ),
                arguments(
                        "edit item: unsupported endpoint",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.editItem()
                                .setScreenName("invalid"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: invalid (provider=VK)")
                        )
                ),
                arguments(
                        "edit item: unsupported provider",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.editItem()
                                .setProvider("twitter"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: vk_public_test (provider=TWITTER)")
                        )
                ),
                arguments(
                        "delete item: valid",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.deleteItem(),
                        List.of(status().isOk())
                ),
                arguments(
                        "delete item: unsupported endpoint",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.deleteItem()
                                .setScreenName("invalid"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: invalid (provider=VK)")
                        )
                ),
                arguments(
                        "delete item: unsupported provider",
                        "/chat/angry/createOrEditItemEvent.json",
                        TestEvent.deleteItem()
                                .setProvider("twitter"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: vk_public_test (provider=TWITTER)")
                        )
                ),
                arguments(
                        "new message: valid",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.newMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "new message: unsupported endpoint",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.newMessage()
                                .setScreenName("invalid"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: invalid (provider=VK)")
                        )
                ),
                arguments(
                        "new message: unsupported provider",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.newMessage()
                                .setProvider("twitter"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: vk_public_test (provider=TWITTER)")
                        )
                ),
                arguments(
                        "edit message: valid",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.editMessage(),
                        List.of(status().isOk())
                ),
                arguments(
                        "edit message: unsupported endpoint",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.editMessage()
                                .setScreenName("invalid"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: invalid (provider=VK)")
                        )
                ),
                arguments(
                        "edit message: unsupported provider",
                        "/chat/angry/createOrEditMessageEvent.json",
                        TestEvent.editMessage()
                                .setProvider("twitter"),
                        List.of(
                                status().is(400),
                                checkException("Unknown chat: vk_public_test (provider=TWITTER)")
                        )
                )
        );
    }

    private static ResultMatcher checkException(String message) {
        return result -> {
            assertNotNull(result.getResolvedException());
            assertEquals(message, result.getResolvedException().getMessage());
        };
    }

    @Test
    public void testChatExceptionHandler() {
        assertNotNull(chatExceptionHandler);
    }

    @MethodSource("eventData")
    @ParameterizedTest(name = "{0}")
    public void testReceiveEvent(String description,
                                 String jsonPath,
                                 TestEvent event,
                                 List<ResultMatcher> expectedResult) throws Exception {
        byte[] content = ResourceHelpers.getResource(jsonPath);
        String contentString = String.format(new String(content),
                event.getEventType(),
                event.getScreenName(),
                event.getProvider(),
                event.getAttachments()
        );
        ResultActions resultActions = mockMvc.perform(
                        post("/v1/angry/item-or-message")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(contentString)
                )
                .andDo(print());
        for (ResultMatcher matcher : expectedResult) {
            resultActions.andExpect(matcher);
        }
    }
}
