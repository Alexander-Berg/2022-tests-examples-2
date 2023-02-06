package ru.yandex.quasar.glagol.impl;

import com.google.gson.Gson;

import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import ru.yandex.quasar.glagol.Config;
import ru.yandex.quasar.glagol.Payload;
import ru.yandex.quasar.glagol.PayloadFactory;
import ru.yandex.quasar.glagol.backend.model.Device;
import ru.yandex.quasar.glagol.backend.model.Devices;
import ru.yandex.quasar.glagol.conversation.model.RepeatMode;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;


public class SerializationTest {
    private static final String COMMAND_PING = "{\"command\":\"ping\"}";
    private static final String COMMAND_VOLUME = "\"command\":\"setVolume\"";
    private static final String COMMAND_PLAYMUSIC = "\"command\":\"playMusic\"";
    private static final String COMMAND_PREV = "\"command\":\"prev\"";
    private static final String COMMAND_NEXT = "\"command\":\"next\"";
    private static final String COMMAND_SHUFFLE = "\"command\":\"shuffle\"";
    private static final String COMMAND_REPEAT = "\"command\":\"repeat\"";

    private final Gson gson = new Gson();
    private final PayloadFactory payloadFactory = new ConnectorImpl(
            new Config.Builder().useDemoMetricaKey().build()).getPayloadFactory();

    @Test
    public void testPayloadSerialization() {
        Payload pingPayload = payloadFactory.getPingPayload();
        String serialized = gson.toJson(pingPayload);
        assertEquals(serialized, COMMAND_PING);
    }

    @Test
    public void testVolumeSerialization() {
        Payload setVolumePayload = payloadFactory.getSetVolumePayload(0.5);
        String serialized = gson.toJson(setVolumePayload);
        assertTrue(serialized.contains(COMMAND_VOLUME));
        assertTrue(serialized.contains("\"volume\":0.5"));
    }

    @Test
    public void testPlayMusicSerialization() {
        Payload playMusicPayload = payloadFactory.getPlayMusicPayload("a", "b");
        String serialized = gson.toJson(playMusicPayload);
        assertTrue(serialized.contains(COMMAND_PLAYMUSIC));
        assertFalse(serialized.contains("startFromId"));
        assertFalse(serialized.contains("startFromPosition"));
        assertFalse(serialized.contains("\"shuffle\":true"));
    }

    @Test
    public void testPlayMusicSerializationExtended() {
        Payload playMusicPayload = payloadFactory.getPlayMusicPayload("a", "b", 0.5, "c", 123);
        String serialized = gson.toJson(playMusicPayload);
        assertTrue(serialized.contains(COMMAND_PLAYMUSIC));
        assertTrue(serialized.contains("startFromId\":\"c\""));
        assertTrue(serialized.contains("startFromPosition\":123"));
        assertFalse(serialized.contains("\"shuffle\":true"));
        assertFalse(serialized.contains("\"repeat\":\"All"));
        assertFalse(serialized.contains("\"repeat\":\"One"));
    }

    @Test
    public void testPlayMusicSerializationFull() {
        Payload playMusicPayload = payloadFactory.getPlayMusicPayload("a", "b", 0.5, "c", 123, "screen-to-start", true, RepeatMode.All);
        String serialized = gson.toJson(playMusicPayload);
        assertTrue(serialized.contains(COMMAND_PLAYMUSIC));
        assertTrue(serialized.contains("type\":\"a\""));
        assertTrue(serialized.contains("id\":\"b\""));
        assertTrue(serialized.contains("startFromId\":\"c\""));
        assertTrue(serialized.contains("startFromPosition\":123"));
        assertTrue(serialized.contains("from\":\"screen-to-start\""));
        assertTrue(serialized.contains("shuffle\":true"));
        assertTrue(serialized.contains("repeat\":\"All\""));

        Payload playMusicPayload2 = payloadFactory.getPlayMusicPayload("b", "a", 0.0, "d", 321, "screen-to-start2", false, RepeatMode.One);
        String serialized2 = gson.toJson(playMusicPayload2);
        assertTrue(serialized2.contains(COMMAND_PLAYMUSIC));
        assertTrue(serialized2.contains("type\":\"b\""));
        assertTrue(serialized2.contains("id\":\"a\""));
        assertTrue(serialized2.contains("startFromId\":\"d\""));
        assertTrue(serialized2.contains("startFromPosition\":321"));
        assertTrue(serialized2.contains("from\":\"screen-to-start2\""));
        assertTrue(serialized2.contains("shuffle\":false"));
        assertTrue(serialized2.contains("repeat\":\"One\""));
    }

    @Test
    public void testPlayRadioSerialization() {
        Payload payload1 = payloadFactory.getPlayRadioPayload("radio-id-1");
        String serialized1 = gson.toJson(payload1);
        assertTrue(serialized1.contains("\"command\":\"playRadio\""));
        assertTrue(serialized1.contains("\"id\":\"radio-id-1\""));

        Payload payload2 = payloadFactory.getPlayRadioPayload("radio-id-2");
        String serialized2 = gson.toJson(payload2);
        assertTrue(serialized2.contains("\"command\":\"playRadio\""));
        assertTrue(serialized2.contains("\"id\":\"radio-id-2\""));
    }

    @Test
    public void testNextCommmandSerializationFull() {

        Payload payload = payloadFactory.getNextPayload(true);
        String serialized = gson.toJson(payload);
        assertTrue(serialized.contains(COMMAND_NEXT));
        assertTrue(serialized.contains("setPause\":true"));
    }

    @Test
    public void testShuffleSerialization() {
        Payload shuffle = payloadFactory.getShufflePayload(true);
        String serialized = gson.toJson(shuffle);
        System.out.println(serialized);
        assertTrue(serialized.contains(COMMAND_SHUFFLE));
        assertTrue(serialized.contains("\"enable\":true"));

        Payload shuffle2 = payloadFactory.getShufflePayload(false);
        String serialized2 = gson.toJson(shuffle2);
        System.out.println(serialized2);
        assertTrue(serialized2.contains(COMMAND_SHUFFLE));
        assertTrue(serialized2.contains("\"enable\":false"));
    }

    @Test
    public void testRepeatSerialization() {
        Payload repeatNone = payloadFactory.getRepeatPayload(RepeatMode.None);
        String serialized = gson.toJson(repeatNone);
        System.out.println(serialized);
        assertTrue(serialized.contains(COMMAND_REPEAT));
        assertTrue(serialized.contains("\"mode\":\"None\""));

        Payload repeatAll = payloadFactory.getRepeatPayload(RepeatMode.All);
        String serialized2 = gson.toJson(repeatAll);
        System.out.println(serialized2);
        assertTrue(serialized2.contains(COMMAND_REPEAT));
        assertTrue(serialized2.contains("\"mode\":\"All\""));

        Payload repeatOne = payloadFactory.getRepeatPayload(RepeatMode.One);
        String serialized3 = gson.toJson(repeatOne);
        System.out.println(serialized3);
        assertTrue(serialized3.contains(COMMAND_REPEAT));
        assertTrue(serialized3.contains("\"mode\":\"One\""));
    }

    @Test
    public void testSoftwareVersionSerialzation() {
        Payload swver = payloadFactory.getSoftwareVersionPayload();
        String serialized = gson.toJson(swver);
        assertTrue(serialized.contains("\"command\":\"softwareVersion\""));
    }

    @Test
    public void testPrevCommmandSerializationFull() {
        Payload payload = payloadFactory.getPrevPayload(true, true);
        String serialized = gson.toJson(payload);
        assertTrue(serialized.contains(COMMAND_PREV));
        assertTrue(serialized.contains("setPause\":true"));
        assertTrue(serialized.contains("forced\":true"));
    }

    @Test
    public void testMessageWrapperSerializationAndDeserialization() {
        Payload pingPayload = payloadFactory.getPingPayload();
        ConversationImpl.SentMessageWrapper wrapper = new ConversationImpl.SentMessageWrapper(pingPayload, "duh");
        String serialized = gson.toJson(wrapper);

        assertTrue(serialized.contains(COMMAND_PING));
        assertTrue(serialized.contains("payload"));
    }

    @Test
    public void testDevicesSerialization() {
        Devices devices = new Devices();
        List<Device> devicesList = new ArrayList<>();
        Device device = new Device();
        device.setPlatform("yandexmodule");
        devicesList.add(device);
        device = new Device();
        device.setPlatform("yandexmodule");
        device.setPromocodeActivated(true);
        device.setActivationCode("HUZZAH!");
        device.setPlatform("b");
        devicesList.add(device);
        devices.setDevices(devicesList);

        String serialized = gson.toJson(devices);
        System.out.println(serialized);
        assertTrue(serialized.contains("promocode_activated"));
        assertTrue(serialized.contains("activation_code"));
    }
}
