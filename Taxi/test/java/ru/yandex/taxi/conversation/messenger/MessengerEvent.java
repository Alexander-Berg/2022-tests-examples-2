package ru.yandex.taxi.conversation.messenger;

public class MessengerEvent {
    public static MessengerEvent inboundTextMessage() {
        return new MessengerEvent();
    }

    public static MessengerEvent deliveryReportMessage() {
        return new MessengerEvent();
    }
}
