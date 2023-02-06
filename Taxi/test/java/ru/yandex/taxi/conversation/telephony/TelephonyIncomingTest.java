package ru.yandex.taxi.conversation.telephony;

import java.nio.file.Files;
import java.util.UUID;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.util.ResourceUtils;

import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyEnvelope;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyServiceContent;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.receive.telephony.exception.UnknownIvrId;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration.JSON_OBJECT_MAPPER;

@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:/telephony/telephony_test.properties")
public class TelephonyIncomingTest extends AbstractFunctionalTest {

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private LogbrokerService logbrokerService;
    @Autowired
    @Qualifier(JSON_OBJECT_MAPPER)
    private ObjectMapper objectMapper;

    @Test
    public void testPositiveIncomingCall() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/incoming/incoming_positive.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.actions", Matchers.hasSize(2)))
                .andExpect(jsonPath("$.actions[*].external_id", Matchers.is(Matchers.notNullValue())))
                .andExpect(jsonPath("$.actions[0].answer").exists())
                .andExpect(jsonPath("$.actions[1].hold").exists());

        var argumentCaptor = ArgumentCaptor.forClass(byte[].class);
        verify(logbrokerService).write(any(), argumentCaptor.capture());

        TelephonyEnvelope envelope = objectMapper.readValue(argumentCaptor.getValue(), TelephonyEnvelope.class);
        assertNotNull(envelope);
        assertNotNull(envelope.getId());
        assertNotNull(envelope.getTimestamp());
        assertNotNull(envelope.getContactPoint());
        assertEquals("+74954143000", envelope.getContactPoint().getId());
        assertEquals(Endpoint.Channel.TELEPHONY, envelope.getContactPoint().getChannel());
        assertNotNull(envelope.getFrom());
        assertEquals("0000061102-7253797153-1651758125-0017524424", envelope.getFrom().getId());
        assertEquals("+79789973155", envelope.getFrom().getUserId());
        assertNull(envelope.getTo());
        assertNotNull(envelope.getService());
        assertEquals(TelephonyServiceContent.Type.INCOMING, envelope.getService().getType());
    }

    @Test
    public void testIncomingWithUnknownIvr() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/incoming/incoming_unknown_ivr.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().is4xxClientError())
                .andExpect(result -> assertTrue(result.getResolvedException() instanceof UnknownIvrId));

        verify(logbrokerService, never()).write(any(), any());
    }

}
