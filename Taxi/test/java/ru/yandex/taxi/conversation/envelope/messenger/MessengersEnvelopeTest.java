package ru.yandex.taxi.conversation.envelope.messenger;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.test.context.junit.jupiter.web.SpringJUnitWebConfig;

import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.ContactPoint;
import ru.yandex.taxi.conversation.envelope.OutEnvelope;
import ru.yandex.taxi.conversation.jackson.nestedtype.JacksonNestedTypeTestConfig;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static ru.yandex.taxi.conversation.jackson.nestedtype.JacksonNestedTypeTestConfig.JACKSON_NESTED_TYPE_TEST_MAPPER_NAME;

@SpringJUnitWebConfig(classes = JacksonNestedTypeTestConfig.class)
public class MessengersEnvelopeTest {

    @Autowired
    @Qualifier(JACKSON_NESTED_TYPE_TEST_MAPPER_NAME)
    private ObjectMapper objectMapper;

    @Test
    public void telegramTextContentSerializationAndDeserialization() throws Exception {

        // arrange
        var originText = new TextContent("aabbcc");
        var originContactPoint = new ContactPoint("id-1", Endpoint.Channel.TELEGRAM);
        var originEnvelope = new TelegramEnvelope();
        originEnvelope.setContactPoint(originContactPoint);
        originEnvelope.setContent(originText);

        // act
        String jsonFromOrigin = objectMapper.writeValueAsString(originEnvelope);
        var deserializedInstance = objectMapper.readValue(jsonFromOrigin, OutEnvelope.class);

        // assert
        assertNotNull(deserializedInstance);
        assertTrue(deserializedInstance instanceof TelegramEnvelope);
        var envelope = (TelegramEnvelope) deserializedInstance;
        assertTrue(envelope.getContent() instanceof TextContent);
        var textContent = (TextContent) envelope.getContent();
        assertEquals(originText.getText(), textContent.getText());
        assertEquals(originText.getType(), textContent.getType());
    }

    @Test
    public void whatsappTextContentSerializationAndDeserialization() throws Exception {

        // arrange
        var originText = new TextContent("aabbcc");
        var originContactPoint = new ContactPoint("id-1", Endpoint.Channel.WHATSAPP);
        var originEnvelope = new WhatsappEnvelope();
        originEnvelope.setContactPoint(originContactPoint);
        originEnvelope.setContent(originText);

        // act
        String jsonFromOrigin = objectMapper.writeValueAsString(originEnvelope);
        var deserializedInstance = objectMapper.readValue(jsonFromOrigin, OutEnvelope.class);

        // assert
        assertNotNull(deserializedInstance);
        assertTrue(deserializedInstance instanceof WhatsappEnvelope);
        var envelope = (WhatsappEnvelope) deserializedInstance;
        assertTrue(envelope.getContent() instanceof TextContent);
        var textContent = (TextContent) envelope.getContent();
        assertEquals(originText.getText(), textContent.getText());
        assertEquals(originText.getType(), textContent.getType());
    }
}
