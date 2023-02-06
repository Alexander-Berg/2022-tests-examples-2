package ru.yandex.taxi.conversation.telephony;

import java.nio.file.Files;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.util.ResourceUtils;

import ru.yandex.market.common.retrofit.ExecuteCall;
import ru.yandex.mj.generated.client.telephony.api.TaxiTelephonyApiClient;
import ru.yandex.mj.generated.client.telephony.model.CallAction;
import ru.yandex.mj.generated.client.telephony.model.CreateCallRequest;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyEnvelope;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyServiceContent;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.read.MessageProcessorService;
import ru.yandex.taxi.conversation.util.LogbrokerMessageHelper;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration.JSON_OBJECT_MAPPER;

@Disabled
@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:/telephony/telephony_test.properties")
public class TelephonyOutgoingTest extends AbstractFunctionalTest {

    private static final String CONSUMER_ID = "/tests/conversation-in-messages-consumer";

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private MessageProcessorService messageProcessorService;
    @Autowired
    private LogbrokerService logbrokerService;
    @Autowired
    @Qualifier(JSON_OBJECT_MAPPER)
    private ObjectMapper objectMapper;
    @MockBean
    private TaxiTelephonyApiClient telephonyApiClient;
    @Value("${endpoint.telephony.taxi.ivrFlowId}")
    private String ivrFlowId;
    @Value("${endpoint.telephony.taxi.externalOutgoingRouteId}")
    private String externalOutgoingRouteId;

    @Test
    public void testPositiveOutgoingCall() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/outgoing/outgoing_positive.json").toPath());

        var call = mock(ExecuteCall.class);
        when(call.scheduleVoid()).thenReturn(mock(CompletableFuture.class));
        when(telephonyApiClient.createCall(any())).thenReturn(call);

        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(content, CONSUMER_ID));

        var argumentCaptor = ArgumentCaptor.forClass(CreateCallRequest.class);
        verify(telephonyApiClient, times(1)).createCall(argumentCaptor.capture());

        CreateCallRequest request = argumentCaptor.getValue();
        assertNotNull(request);
        assertEquals("xxxx-xxxx-xxxx-xxxx", request.getCallExternalId());
        assertEquals(ivrFlowId, request.getIvrFlowId());

        List<CallAction> actions = request.getActions();
        assertNotNull(actions);
        assertEquals(2, actions.size());

        var originate = request.getActions().get(0);
        assertNotNull(originate.getOriginate());
        assertEquals("msg-id-xxxx", originate.getExternalId());
        assertEquals("+79997775522", originate.getOriginate().getPhoneNumber());
        assertEquals(externalOutgoingRouteId, originate.getOriginate().getRoute());
        assertEquals(10, originate.getOriginate().getTimeoutSec());
        assertEquals("88001000200", originate.getOriginate().getOutboundNumber());

        var forward = request.getActions().get(1);
        assertNotNull(forward.getForward());
        assertNotNull(forward.getExternalId());
        assertEquals("operator_vasya", forward.getForward().getYandexUid());
        assertNull(forward.getForward().getPhoneNumber());
    }

    @Test
    public void testPositiveOutgoingNotify() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/outgoing/outgoing_notify_positive.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isEmpty());

        var argumentCaptor = ArgumentCaptor.forClass(byte[].class);
        verify(logbrokerService).write(any(), argumentCaptor.capture());

        TelephonyEnvelope envelope = objectMapper.readValue(argumentCaptor.getValue(), TelephonyEnvelope.class);

        assertNotNull(envelope.getId());
        assertDoesNotThrow(() -> UUID.fromString(envelope.getId()));
        assertNotNull(envelope.getTimestamp());

        var contactPoint = envelope.getContactPoint();
        assertNotNull(contactPoint);
        assertEquals("88001000200", contactPoint.getId());
        assertEquals(Endpoint.Channel.TELEPHONY, contactPoint.getChannel());

        var from = envelope.getFrom();
        assertNotNull(from);
        assertEquals("xxxx-xxxx-xxxx-xxxx", from.getId());
        assertEquals("+79997775522", from.getUserId());

        assertNull(envelope.getTo());

        var service = envelope.getService();
        assertNotNull(service);
        assertEquals(TelephonyServiceContent.Type.CONNECTED, service.getType());
    }
}
