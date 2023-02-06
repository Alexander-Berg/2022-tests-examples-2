package ru.yandex.taxi.conversation.verticals;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.OffsetDateTime;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.InvalidProtocolBufferException;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.test.context.TestPropertySource;
import org.springframework.util.ResourceUtils;

import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.verticals.VerticalsEnvelope;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.read.MessageProcessorService;
import ru.yandex.taxi.conversation.proto.ChatPayload;
import ru.yandex.taxi.conversation.proto.Contact;
import ru.yandex.taxi.conversation.proto.File;
import ru.yandex.taxi.conversation.proto.Message;
import ru.yandex.taxi.conversation.util.LogbrokerMessageHelper;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration.JSON_OBJECT_MAPPER;

@TestPropertySource(locations = "classpath:/verticals/verticals_test.properties")
public class VerticalsIncomingTest extends AbstractFunctionalTest {

    private static final String CONSUMER_ID = "/tests/verticals-messages-consumer";
    private static final String PARTITION = "rt3.kafka-bs--conversation@development--verticals-to-conversation";

    @Autowired
    private MessageProcessorService messageProcessorService;
    @Autowired
    private LogbrokerService logbrokerService;
    @Autowired
    @Qualifier(JSON_OBJECT_MAPPER)
    private ObjectMapper objectMapper;

    private void prepareFile() throws IOException {
        Message message = Message.newBuilder()
                .setMessageId("positive_test_1")
                .setFrom(Contact.newBuilder().setContactId("user_1").build())
                .setTo(Contact.newBuilder().setContactId("support_chat_1").build())
                .setChatPayload(ChatPayload.newBuilder()
                        .setText("hello").setReplyToId("test_0")
                        .addFiles(File.newBuilder().setUrl("http://test.test").build())
                        .build())
                .build();

        Files.write(Path.of("positive.bin"), message.toByteArray(), StandardOpenOption.CREATE_NEW);
    }

    @Test
    public void testPositiveIncomingMessage() throws Exception {
        byte[] message = Files.readAllBytes(
                ResourceUtils.getFile("classpath:verticals/incoming/incoming_positive.bin").toPath());
        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(message, CONSUMER_ID, PARTITION));

        var bytesCaptor = ArgumentCaptor.forClass(byte[].class);
        verify(logbrokerService).write(any(), bytesCaptor.capture());

        VerticalsEnvelope envelope = assertDoesNotThrow(() ->
                objectMapper.readValue(bytesCaptor.getValue(), VerticalsEnvelope.class));

        assertEquals("positive_test_1", envelope.getId());
        assertNotNull(envelope.getTimestamp());
        assertTrue(OffsetDateTime.now().minusSeconds(60).isBefore(envelope.getTimestamp()));

        var contactPoint = envelope.getContactPoint();
        assertNotNull(contactPoint);
        assertEquals(Endpoint.Channel.VERTICALS, contactPoint.getChannel());
        assertEquals("verticals-test", contactPoint.getId());

        var from = envelope.getFrom();
        assertNotNull(from);
        assertEquals("user_1", from.getId());

        var to = envelope.getTo();
        assertNotNull(to);
        assertEquals("support_chat_1", to.getId());

        var content = envelope.getContent();
        assertNotNull(content);
        assertEquals("hello", content.getText());
        assertEquals("test_0", content.getReplyToId());
        assertEquals(1, content.getFilesCount());

        var files = content.getFiles();
        assertNotNull(files);
        assertFalse(files.isEmpty());
        assertEquals(1, files.size());
        assertEquals("http://test.test", files.get(0));
    }

    @Test
    public void testSkipBrokenOrUnknownIncomingMessage() throws Exception {
        byte[] message = Files.readAllBytes(
                ResourceUtils.getFile("classpath:verticals/incoming/incoming_broken_message.bin").toPath());

        assertThrows(InvalidProtocolBufferException.class, () -> Message.parseFrom(message));

        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(message, CONSUMER_ID, PARTITION));

        verifyNoInteractions(logbrokerService);
    }
}