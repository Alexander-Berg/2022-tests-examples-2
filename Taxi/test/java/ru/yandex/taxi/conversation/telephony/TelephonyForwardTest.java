package ru.yandex.taxi.conversation.telephony;

import java.nio.file.Files;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.util.ResourceUtils;

import ru.yandex.market.common.retrofit.ExecuteCall;
import ru.yandex.mj.generated.client.telephony.api.TaxiTelephonyApiClient;
import ru.yandex.mj.generated.client.telephony.model.AppendCallScriptRequest;
import ru.yandex.mj.generated.client.telephony.model.CallAction;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyEnvelope;
import ru.yandex.taxi.conversation.envelope.telephony.TelephonyServiceContent;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.read.MessageProcessorService;
import ru.yandex.taxi.conversation.util.LogbrokerMessageHelper;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@TestPropertySource(locations = "classpath:/telephony/telephony_test.properties")
public class TelephonyForwardTest extends AbstractFunctionalTest {

    private static final String CONSUMER_ID = "/tests/conversation-in-messages-consumer";

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private MessageProcessorService messageProcessorService;
    @Autowired
    private LogbrokerService logbrokerService;
    @Autowired
    private ObjectMapper objectMapper;
    @MockBean
    private TaxiTelephonyApiClient telephonyApiClient;
    @Value("${endpoint.telephony.taxi.ivrFlowId}")
    private String ivrFlowId;

    @Test
    public void testPositiveForwardCommandYuid() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_yuid_positive.json").toPath());

        var call = mock(ExecuteCall.class);
        when(call.scheduleVoid()).thenReturn(mock(CompletableFuture.class));
        when(telephonyApiClient.appendCallScript(any(), any(), any())).thenReturn(call);

        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(content, CONSUMER_ID));

        var callIdCaptor = ArgumentCaptor.forClass(String.class);
        var ivrFlowIdCaptor = ArgumentCaptor.forClass(String.class);
        var callScriptCaptor = ArgumentCaptor.forClass(AppendCallScriptRequest.class);
        verify(telephonyApiClient, times(1))
                .appendCallScript(callIdCaptor.capture(), ivrFlowIdCaptor.capture(), callScriptCaptor.capture());

        assertEquals("0000061102-7253797153-1651758125-0017534424", callIdCaptor.getValue());
        assertEquals(ivrFlowId, ivrFlowIdCaptor.getValue());

        AppendCallScriptRequest script = callScriptCaptor.getValue();
        assertNotNull(script);

        List<CallAction> actions = script.getActions();
        assertNotNull(actions);
        assertEquals(2, actions.size());

        var forward = script.getActions().get(0);
        assertNotNull(forward.getForward());
        assertEquals("msg-id-xxxx", forward.getExternalId());
        assertEquals("operator_vasya", forward.getForward().getYandexUid());
        assertEquals("test_route", forward.getForward().getRoute());
        assertEquals(15, forward.getForward().getTimeoutSec());
        assertNull(forward.getForward().getPhoneNumber());

        var hold = script.getActions().get(1);
        assertNotNull(hold.getExternalId());
        assertNotNull(hold.getHold());
    }

    @Test
    public void testPositiveForwardCommandPhone() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_phone_positive.json").toPath());

        var call = mock(ExecuteCall.class);
        when(call.scheduleVoid()).thenReturn(mock(CompletableFuture.class));
        when(telephonyApiClient.appendCallScript(any(), any(), any())).thenReturn(call);

        messageProcessorService.processMessage(LogbrokerMessageHelper.createMessage(content, CONSUMER_ID));

        var callIdCaptor = ArgumentCaptor.forClass(String.class);
        var ivrFlowIdCaptor = ArgumentCaptor.forClass(String.class);
        var callScriptCaptor = ArgumentCaptor.forClass(AppendCallScriptRequest.class);
        verify(telephonyApiClient, times(1))
                .appendCallScript(callIdCaptor.capture(), ivrFlowIdCaptor.capture(), callScriptCaptor.capture());

        assertEquals("0000061102-7253797153-1651758125-0017534424", callIdCaptor.getValue());
        assertEquals(ivrFlowId, ivrFlowIdCaptor.getValue());

        AppendCallScriptRequest script = callScriptCaptor.getValue();
        assertNotNull(script);

        List<CallAction> actions = script.getActions();
        assertNotNull(actions);
        assertEquals(2, actions.size());

        var forward = script.getActions().get(0);
        assertNotNull(forward.getForward());
        assertEquals("msg-id-xxxx", forward.getExternalId());
        assertEquals("+79995556655", forward.getForward().getPhoneNumber());
        assertEquals("test_route", forward.getForward().getRoute());
        assertEquals(15, forward.getForward().getTimeoutSec());
        assertNull(forward.getForward().getYandexUid());

        var hold = script.getActions().get(1);
        assertNotNull(hold.getExternalId());
        assertNotNull(hold.getHold());
    }

    @Test
    public void testForwardConnectedYuid() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_connected_yuid.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isEmpty());

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
        assertEquals("0000061102-7253797153-1651758125-0017524400", envelope.getFrom().getId());
        assertEquals("+79789973369", envelope.getFrom().getUserId());
        assertNull(envelope.getTo());
        assertNotNull(envelope.getService());
        assertEquals(TelephonyServiceContent.Type.CONNECTED, envelope.getService().getType());
        assertEquals("1120000000462462", envelope.getService().getYuid());
        assertNull(envelope.getService().getRoute());
        assertNull(envelope.getService().getPhoneNumber());
    }

    @Test
    public void testForwardConnectedPhone() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_connected_phone.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isEmpty());

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
        assertEquals("0000061102-7253797153-1651758125-0017524400", envelope.getFrom().getId());
        assertEquals("+79789973369", envelope.getFrom().getUserId());
        assertNull(envelope.getTo());
        assertNotNull(envelope.getService());
        assertEquals(TelephonyServiceContent.Type.CONNECTED, envelope.getService().getType());
        assertNull(envelope.getService().getYuid());
        assertEquals("outside_world", envelope.getService().getRoute());
        assertEquals("+79999874512", envelope.getService().getPhoneNumber());
    }

    @Test
    public void testForwardFailYuid() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_fail_yuid.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.actions[*].external_id", Matchers.is(Matchers.notNullValue())))
                .andExpect(jsonPath("$.actions[0].hold").exists());

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
        assertEquals("0000061102-7253797153-1651758125-0017524400", envelope.getFrom().getId());
        assertEquals("+79789973369", envelope.getFrom().getUserId());
        assertNull(envelope.getTo());
        assertNotNull(envelope.getService());
        assertEquals(TelephonyServiceContent.Type.FORWARD, envelope.getService().getType());
        assertEquals(TelephonyServiceContent.Status.FAIL, envelope.getService().getStatus());
        assertEquals("1120000000462462", envelope.getService().getYuid());
        assertNull(envelope.getService().getRoute());
        assertNull(envelope.getService().getPhoneNumber());
    }

    @Test
    public void testForwardFailPhone() throws Exception {

        byte[] content = Files.readAllBytes(
                ResourceUtils.getFile("classpath:telephony/forward/forward_fail_phone.json").toPath());

        mockMvc.perform(post("/v1/ivr-framework/call-notify")
                        .header("X-Idempotency-Token", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON_UTF8)
                        .content(content))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.actions[*].external_id", Matchers.is(Matchers.notNullValue())))
                .andExpect(jsonPath("$.actions[0].hold").exists());

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
        assertEquals("0000061102-7253797153-1651758125-0017524400", envelope.getFrom().getId());
        assertEquals("+79789973369", envelope.getFrom().getUserId());
        assertNull(envelope.getTo());
        assertNotNull(envelope.getService());
        assertEquals(TelephonyServiceContent.Type.FORWARD, envelope.getService().getType());
        assertEquals(TelephonyServiceContent.Status.FAIL, envelope.getService().getStatus());
        assertNull(envelope.getService().getYuid());
        assertEquals("outside_world", envelope.getService().getRoute());
        assertEquals("+79999874512", envelope.getService().getPhoneNumber());
    }
}
