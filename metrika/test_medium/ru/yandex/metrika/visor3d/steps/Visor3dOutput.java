package ru.yandex.metrika.visor3d.steps;

import java.util.List;
import java.util.stream.Collectors;

import ru.yandex.metrika.wv2.proto.LogbrokerMessages.LogbrokerMessage;

import static java.util.Comparator.comparing;

public class Visor3dOutput {

    Boolean eventsTableEmpty;

    List<EventPacket> events;

    List<WebVisor2> webVisorEvents;

    List<ScrollPacket> scrolls;

    List<LogbrokerMessage> logbrokerMessages;

    public Visor3dOutput withEventsTableEmpty(Boolean eventsTableEmpty) {
        this.eventsTableEmpty = eventsTableEmpty;
        return this;
    }

    public Visor3dOutput withEvents(List<EventPacket> events) {
        this.events = events;
        return this;
    }

    public Visor3dOutput withWebVisorEvents(List<WebVisor2> webVisorEvents) {
        this.webVisorEvents = webVisorEvents;
        return this;
    }

    public Visor3dOutput withScrolls(List<ScrollPacket> scrolls) {
        this.scrolls = scrolls;
        return this;
    }

    public List<EventPacket> getEvents() {
        return events;
    }

    public List<LogbrokerMessage> getLogbrokerMessages() {
        return logbrokerMessages;
    }

    public List<WebVisor2> getWebVisorEvents() {
        return webVisorEvents.stream().sorted(comparing(WebVisor2::hashCode)).collect(Collectors.toList());
    }

    public List<ScrollPacket> getScrolls() {
        return scrolls.stream().sorted(comparing(ScrollPacket::hashCode)).collect(Collectors.toList());
    }

    public Boolean getEventsTableEmpty() {
        return eventsTableEmpty;
    }

    public Visor3dOutput withLogbrokerMessages(List<LogbrokerMessage> logbrokerMessages) {
        this.logbrokerMessages = logbrokerMessages;
        return this;
    }

}
