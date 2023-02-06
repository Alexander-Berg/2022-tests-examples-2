package ru.yandex.taxi.conversation.chat;

import java.time.OffsetDateTime;
import java.util.List;

import ru.yandex.taxi.conversation.envelope.ContactPoint;
import ru.yandex.taxi.conversation.envelope.chat.ChatAttachment;
import ru.yandex.taxi.conversation.envelope.chat.ChatContent;
import ru.yandex.taxi.conversation.envelope.chat.ChatEnvelope;
import ru.yandex.taxi.conversation.envelope.chat.ChatFromDto;
import ru.yandex.taxi.conversation.envelope.chat.ChatServiceContent;
import ru.yandex.taxi.conversation.envelope.chat.ChatToDto;
import ru.yandex.taxi.conversation.envelope.chat.DirectChatAttachment;
import ru.yandex.taxi.conversation.envelope.chat.MdsChatAttachment;
import ru.yandex.taxi.conversation.envelope.chat.UrlChatAttachment;
import ru.yandex.taxi.conversation.utils.Collections;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ChatEnvelopeHelper {

    public static void assertEqualsEnvelope(ChatEnvelope expected, ChatEnvelope actual, boolean isNew) {
        assertEquals(expected.getId(), actual.getId());
        assertNotNull(actual.getTimestamp());
        if (isNew) {
            assertTrue(expected.getTimestamp().isEqual(actual.getTimestamp()));
        } else {
            assertTrue(actual.getTimestamp().isBefore(OffsetDateTime.now().plusSeconds(10)));
            assertTrue(actual.getTimestamp().isAfter(OffsetDateTime.now().minusSeconds(10)));
        }
        assertEqualsContactPoint(expected.getContactPoint(), actual.getContactPoint());
        assertEqualsFrom(expected.getFrom(), actual.getFrom());
        assertEqualsTo(expected.getTo(), actual.getTo());
        assertEqualsService(expected.getService(), actual.getService());
        assertEqualsContent(expected.getContent(), actual.getContent());
    }

    private static void assertEqualsContactPoint(ContactPoint expected, ContactPoint actual) {
        assertEquals(expected.getId(), actual.getId());
        assertEquals(expected.getChannel(), actual.getChannel());
    }

    private static void assertEqualsFrom(ChatFromDto expected, ChatFromDto actual) {
        if (expected == null) {
            assertNull(actual);
            return;
        }
        assertNotNull(actual);
        assertEquals(expected.getId(), actual.getId());
        assertEquals(expected.getUserId(), actual.getUserId());
        assertEquals(expected.getUserName(), actual.getUserName());
    }

    private static void assertEqualsTo(ChatToDto expected, ChatToDto actual) {
        if (expected == null) {
            assertNull(actual);
            return;
        }
        assertNotNull(actual);
        assertEquals(expected.getId(), actual.getId());
    }

    private static void assertEqualsService(ChatServiceContent expected, ChatServiceContent actual) {
        if (expected == null) {
            assertNull(actual);
            return;
        }
        assertNotNull(actual);
        assertEquals(expected.getType(), actual.getType());
        assertEquals(expected.getMessageId(), actual.getMessageId());
    }

    private static void assertEqualsContent(ChatContent expected, ChatContent actual) {
        if (expected == null) {
            assertNull(actual);
            return;
        }
        assertNotNull(actual);
        assertEquals(expected.getText(), actual.getText());
        assertEquals(expected.getReplyToId(), actual.getReplyToId());
        assertEqualsAttachments(expected.getAttachments(), actual.getAttachments());
    }

    private static void assertEqualsAttachments(List<ChatAttachment> expected, List<ChatAttachment> actual) {
        if (Collections.isEmpty(expected)) {
            assertTrue(Collections.isEmpty(actual));
            return;
        }
        assertNotNull(actual);
        assertEquals(expected.size(), actual.size());
        for (int i = 0; i < expected.size(); i++) {
            assertEqualsAttachment(expected.get(i), actual.get(i));
        }
    }

    private static void assertEqualsAttachment(ChatAttachment expected, ChatAttachment actual) {
        assertEquals(expected.getType(), actual.getType());
        switch (expected.getType()) {
            case link:
                MdsChatAttachment linkExpected = (MdsChatAttachment) expected;
                MdsChatAttachment linkActual = (MdsChatAttachment) actual;
                assertEquals(linkExpected.getId(), linkActual.getId());
                assertEquals(linkExpected.getName(), linkActual.getName());
                assertEquals(linkExpected.getContentType(), linkActual.getContentType());
                assertEquals(linkExpected.getUrl(), linkActual.getUrl());
                assertEquals(linkExpected.getSize(), linkActual.getSize());
                assertEquals(linkExpected.getMdsBucketName(), linkActual.getMdsBucketName());
                assertEquals(linkExpected.getMdsKey(), linkActual.getMdsKey());
                break;
            case url:
                UrlChatAttachment urlExpected = (UrlChatAttachment) expected;
                UrlChatAttachment urlActual = (UrlChatAttachment) actual;
                assertEquals(urlExpected.getName(), urlActual.getName());
                assertEquals(urlExpected.getUrl(), urlActual.getUrl());
                break;
            case direct:
                DirectChatAttachment directExpected = (DirectChatAttachment) expected;
                DirectChatAttachment directActual = (DirectChatAttachment) actual;
                assertEquals(directExpected.getName(), directActual.getName());
                assertEquals(directExpected.getContentType(), directActual.getContentType());
                assertEquals(directExpected.getUrl(), directActual.getUrl());
                break;
        }
    }
}
