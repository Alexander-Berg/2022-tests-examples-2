package ru.yandex.metrika.mobmet.push.common.internal.fcm;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.Test;

import static org.junit.Assert.assertNull;

public class FcmSenderTest {

    @Test
    public void deserializeFcmResponse() throws JsonProcessingException {
        String content = "{\"multicast_id\":5641431956016779661,\"success\":1,\"failure\":0,\"canonical_ids\":0," +
                "\"results\":[{\"message_id\":\"0:1639556842308240%4907602ef9fd7ecd\"}]}";
        FcmSender.FcmResponse fcmResponse = FcmSender.deserializeFcmResponse(content);
        assertNull(fcmResponse.getResults().get(0).getError());
    }
}
