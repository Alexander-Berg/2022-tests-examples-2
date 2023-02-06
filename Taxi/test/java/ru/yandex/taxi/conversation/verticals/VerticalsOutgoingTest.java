package ru.yandex.taxi.conversation.verticals;

import java.nio.file.Files;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;
import org.springframework.util.ResourceUtils;

import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.LogbrokerSessionIdentity;
import ru.yandex.taxi.conversation.logbroker.read.MessageProcessorService;
import ru.yandex.taxi.conversation.proto.File;
import ru.yandex.taxi.conversation.proto.Message;
import ru.yandex.taxi.conversation.util.LogbrokerMessageHelper;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.verify;

@TestPropertySource(locations = "classpath:/verticals/verticals_test.properties")
public class VerticalsOutgoingTest extends AbstractFunctionalTest {

    private static final String CONSUMER_ID = "/tests/conversation-in-messages-consumer";
    private static final String PARTITION = "rt3.kafka-bs--conversation@development--conversation-in-messages";

    @Autowired
    private MessageProcessorService messageProcessorService;
    @Autowired
    private LogbrokerService logbrokerService;

    @Test
    public void testPositiveOutgoingMessage() throws Exception {

        byte[] envelope = Files.readAllBytes(
                ResourceUtils.getFile("classpath:verticals/outgoing/outgoing_positive.json").toPath());
        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(envelope, CONSUMER_ID, PARTITION));

        var bytesCaptor = ArgumentCaptor.forClass(byte[].class);
        var sessionCaptor = ArgumentCaptor.forClass(LogbrokerSessionIdentity.class);
        verify(logbrokerService).write(sessionCaptor.capture(), bytesCaptor.capture());

        var sessionIdentity = sessionCaptor.getValue();
        assertEquals("/tests/conversation-to-verticals", sessionIdentity.getTopic());
        assertEquals("VERTICALS::verticals::verticals-test", sessionIdentity.getSourceId());

        Message message = assertDoesNotThrow(() -> Message.parseFrom(bytesCaptor.getValue()));

        assertEquals("positive_test_2", message.getMessageId());

        var from = message.getFrom();
        assertNotNull(from);
        assertEquals("support_chat_1", from.getContactId());

        var to = message.getTo();
        assertNotNull(to);
        assertEquals("user_1", to.getContactId());

        var chatPayload = message.getChatPayload();
        assertNotNull(chatPayload);
        assertEquals("world", chatPayload.getText());
        assertEquals("positive_test_1", chatPayload.getReplyToId());
        assertEquals(2, chatPayload.getFilesCount());

        var files = chatPayload.getFilesList();
        assertNotNull(files);
        assertFalse(files.isEmpty());
        assertEquals(2, files.size());
        assertEquals(
                Set.of("http://tst1.tst", "http://tst2.tst"),
                files.stream().map(File::getUrl).collect(Collectors.toSet()));
    }

}
