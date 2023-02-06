package ru.yandex.quasar.app.utils;

import androidx.annotation.NonNull;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.commons.lang.StringUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.Collection;
import java.util.List;

import ru.yandex.quasar.protobuf.ModelObjects;
import ru.yandex.quasar.protobuf.QuasarProto;

import static junit.framework.TestCase.assertTrue;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.fail;
import static ru.yandex.quasar.app.utils.VinsUtils.CARD_TYPE_DIV;
import static ru.yandex.quasar.app.utils.VinsUtils.CARD_TYPE_DIV2;

@RunWith(value = AndroidJUnit4.class)
public class VinsUtilsTest {
    private ModelObjects.PushNotification.Builder pushBuilder;

    @Before
    public void init() {
        pushBuilder = ModelObjects.PushNotification.newBuilder();
    }

    @NonNull
    private JSONObject buildVinsResponseObject(JSONObject body) {
        return buildVinsResponseObject(body, null);
    }

    @NonNull
    private JSONObject buildVinsResponseObject(JSONObject body, JSONObject templates) {
        try {
            JSONObject card = new JSONObject();
            card.put("body", body);
            card.put("type", null != templates ? CARD_TYPE_DIV2 : CARD_TYPE_DIV);

            JSONObject vins = new JSONObject();
            vins.put("card", card);
            if (null != templates) {
                vins.put("templates", templates);
            }
            return vins;
        } catch (JSONException ex) {
            System.out.println(ex.getMessage());
            return new JSONObject();
        }
    }

    private void checkDivBody(String expected, String actual) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            assertEquals(mapper.readTree(expected), mapper.readTree(actual));
        } catch (Exception ex) {
            fail();
        }
    }

    @Test
    public void getEmptyVinsCard() {
        String result = VinsUtils.getDivCardFromVins(new JSONObject());
        assertTrue("div card was not set", StringUtils.isEmpty(result));
    }

    @Test
    public void getEmptyDivCard() {
        JSONObject vins = buildVinsResponseObject(new JSONObject());

        String result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div card was set", StringUtils.isNotEmpty(result));
        assertEquals("div body was enriched", "{}", result);
    }

    @Test
    public void getDivCard() throws JSONException {
        JSONObject card = new JSONObject();
        card.put("may", "the force be with you");
        JSONObject vins = buildVinsResponseObject(card);

        String result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div card was set", StringUtils.isNotEmpty(result));
        checkDivBody("{\"may\":\"the force be with you\"}", result);
    }

    @Test
    public void getEmptyDiv2Card() {
        JSONObject vins = buildVinsResponseObject(new JSONObject(), new JSONObject());

        String result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was set", StringUtils.isNotEmpty(result));
        checkDivBody("{\"card\":{}, \"templates\":{}}", result);
    }

    @Test
    public void getWrongDiv2Card() throws JSONException {
        JSONObject vins = buildVinsResponseObject(new JSONObject(), new JSONObject());
        vins.remove("card");

        String result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 1", StringUtils.isEmpty(result));

        vins.put("card", null);
        result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 2", StringUtils.isEmpty(result));

        vins.put("card", new JSONObject()); // should have body and type inside
        result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 3", StringUtils.isEmpty(result));

        JSONObject card = new JSONObject();
        card.put("type", "SOME TYPE");
        vins.put("card", card); // should have proper div card type inside
        result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 4", StringUtils.isEmpty(result));

        card = new JSONObject();
        card.put("type", CARD_TYPE_DIV2);
        card.put("body", null);
        vins.put("card", card); // should have proper body inside
        result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 5", StringUtils.isEmpty(result));

        card = new JSONObject();
        card.put("type", CARD_TYPE_DIV2);
        card.put("body", new JSONObject()); // proper body
        vins.put("card", card);
        vins.remove("templates"); // but without templates
        result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was not set 6", StringUtils.isEmpty(result));
    }

    @Test
    public void getDiv2Card() throws JSONException {
        JSONObject card = new JSONObject();
        card.put("may", "the force be with you");
        JSONObject template = new JSONObject();
        template.put("master", "yoda");
        JSONObject vins = buildVinsResponseObject(card, template);

        String result = VinsUtils.getDivCardFromVins(vins);
        assertTrue("div2 card was set", StringUtils.isNotEmpty(result));

        final String expected = "{\"card\":{\"may\":\"the force be with you\"}," +
                "\"templates\":{\"master\":\"yoda\"}}";
        checkDivBody(expected, result);
    }

    @Test
    public void checkEmptyPush() {
        ModelObjects.PushNotification push = pushBuilder.build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty states", 0, aliceStates.size());
    }

    @Test
    public void checkPushPhrase() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        final String phrase = "I'm your father";
        payload.put("phrase", phrase);
        message.put("payload", payload);

        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got only one state", 1, aliceStates.size());

        ModelObjects.AliceState state = aliceStates.iterator().next();
        assertEquals("state type", ModelObjects.AliceState.State.LISTENING, state.getState());
        assertEquals("state phrase", phrase, state.getRecognizedPhrase());
    }

    @Test
    public void checkPushWrongSuggests() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        payload.put("suggest", "");
        message.put("payload", payload);
        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty states 1", 0, aliceStates.size());

        payload.put("suggest", "[]");
        message.put("payload", payload);
        push = pushBuilder.setMessage(message.toString()).build();
        aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty states 2", 0, aliceStates.size());

        payload.put("suggest", new JSONArray());
        message.put("payload", payload);
        push = pushBuilder.setMessage(message.toString()).build();
        aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty states 3", 0, aliceStates.size());

        payload.put("suggest", new JSONObject());
        message.put("payload", payload);
        push = pushBuilder.setMessage(message.toString()).build();
        aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty states 4", 0, aliceStates.size());
    }

    @Test
    public void checkPushCorrectSuggests() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        JSONArray array = new JSONArray();

        array.put("Suggest 0");
        array.put("Suggest 1");
        array.put("Suggest 2");

        payload.put("suggest", array);
        message.put("payload", payload);
        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got only one state", 1, aliceStates.size());

        ModelObjects.AliceState state = aliceStates.iterator().next();
        assertEquals("state type", ModelObjects.AliceState.State.SPEAKING, state.getState());

        assertNotNull("vins response not null", state.getVinsResponse());
        List<ModelObjects.VinsResponse.Suggest> list = state.getVinsResponse().getSuggestsList();
        assertNotNull("suggests not null", list);
        assertEquals("suggests count", 3, list.size());
        for (int i = 0; i < 3; i++ ) {
            ModelObjects.VinsResponse.Suggest suggest = list.get(i);
            assertEquals(String.format("Suggest %d", i), suggest.getText());
        }
    }

    @Test
    public void checkPushNonStringSuggests() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        JSONArray array = new JSONArray();

        array.put(0);
        array.put(1);
        array.put(2);
        array.put(null);

        payload.put("suggest", array);
        message.put("payload", payload);
        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got only one state", 1, aliceStates.size());

        ModelObjects.AliceState state = aliceStates.iterator().next();
        assertEquals("state type", ModelObjects.AliceState.State.SPEAKING, state.getState());

        assertNotNull("vins response not null", state.getVinsResponse());
        List<ModelObjects.VinsResponse.Suggest> list = state.getVinsResponse().getSuggestsList();
        assertNotNull("suggests not null", list);
        assertEquals("suggests count", 4, list.size());
        for (int i = 0; i < 4; i++ ) {
            ModelObjects.VinsResponse.Suggest suggest = list.get(i);
            if (i != 3) {
                assertEquals(String.format("%d", i), suggest.getText());
            } else {
                assertEquals("null", suggest.getText());
            }
        }
    }

    @Test
    public void checkPushWrongCard() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        payload.put("card", null);
        message.put("payload", payload);
        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got empty state", 0, aliceStates.size());
    }

    @Test
    public void checkPushCorrectCard() throws JSONException {
        JSONObject message = new JSONObject();
        JSONObject payload = new JSONObject();
        JSONObject card = new JSONObject();

        card.put("hello", "world");
        payload.put("card", card);
        message.put("payload", payload);
        ModelObjects.PushNotification push = pushBuilder.setMessage(message.toString()).build();
        Collection<ModelObjects.AliceState> aliceStates = VinsUtils.getAliceStates(push);
        assertNotNull("states not null", aliceStates);
        assertEquals("got only one state", 1, aliceStates.size());

        ModelObjects.AliceState state = aliceStates.iterator().next();
        assertEquals("state type", ModelObjects.AliceState.State.SPEAKING, state.getState());
        assertNotNull("vins response not null", state.getVinsResponse());

        String divCard = state.getVinsResponse().getDivCard();
        assertEquals("div card", "{\"hello\":\"world\"}", divCard);
    }
}
