package ru.yandex.taxi.conversation.chat.angry;

import java.util.List;

import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.handle.chat.angry.SmmObjectEventType;
import ru.yandex.taxi.conversation.util.ResourceHelpers;

public class TestEvent {

    private String eventType;
    private String screenName = "vk_public_test";
    private String provider = "vk";
    private Endpoint.Channel channel;
    private String attachments = "[]";
    private List<String> attachmentUrlsForMds = List.of();

    public TestEvent(String eventType) {
        this.eventType = eventType;
    }

    public static TestEvent newItem() {
        return new TestEvent(SmmObjectEventType.ITEM_NEW.getValue());
    }

    public static TestEvent editItem() {
        return new TestEvent(SmmObjectEventType.ITEM_EDIT.getValue());
    }

    public static TestEvent deleteItem() {
        return new TestEvent(SmmObjectEventType.ITEM_DELETE.getValue());
    }

    public static TestEvent newMessage() {
        return new TestEvent(SmmObjectEventType.MESSAGE_NEW.getValue());
    }

    public static TestEvent editMessage() {
        return new TestEvent(SmmObjectEventType.MESSAGE_EDIT.getValue());
    }

    public String getEventType() {
        return eventType;
    }

    public TestEvent setEventType(String eventType) {
        this.eventType = eventType;
        return this;
    }

    public String getScreenName() {
        return screenName;
    }

    public TestEvent setScreenName(String screenName) {
        this.screenName = screenName;
        return this;
    }

    public String getProvider() {
        return provider;
    }

    public TestEvent setProvider(String provider) {
        this.provider = provider;
        return this;
    }

    public Endpoint.Channel getChannel() {
        return channel;
    }

    public TestEvent setChannel(Endpoint.Channel channel) {
        this.channel = channel;
        return this;
    }

    public String getAttachments() {
        return attachments;
    }

    public TestEvent setAttachments(String attachmentsPath) {
        this.attachments = new String(ResourceHelpers.getResource(attachmentsPath));
        return this;
    }

    public List<String> getAttachmentUrlsForMds() {
        return attachmentUrlsForMds;
    }

    public TestEvent setAttachmentUrlsForMds(List<String> attachmentUrlsForMds) {
        this.attachmentUrlsForMds = attachmentUrlsForMds;
        return this;
    }
}
