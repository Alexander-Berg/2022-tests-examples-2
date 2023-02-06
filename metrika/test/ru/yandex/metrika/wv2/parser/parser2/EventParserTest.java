package ru.yandex.metrika.wv2.parser.parser2;

import java.io.IOException;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.ui.webvisor.player2.PackageExternal;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.events.Event;
import ru.yandex.metrika.wv2.events.EventType;
import ru.yandex.metrika.wv2.events.FatalErrorEventMetadata;
import ru.yandex.metrika.wv2.events.Keystrokes;
import ru.yandex.metrika.wv2.events.PageMeta;
import ru.yandex.metrika.wv2.parser.EventParser;
import ru.yandex.metrika.wv2.parser.Package;
import ru.yandex.metrika.wv2.parser.State2;
import ru.yandex.metrika.wv2.parser.WVFatalErrorEventException;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;

public class EventParserTest {

    private EventParser eventParser;

    @Before
    public void setUp() throws Exception {
        eventParser = new SomeEventParser();
    }

    @Test
    public void validationThrowsExceptionWhenFatalErrorEvent() {
        assertThatThrownBy(() -> eventParser.validate(getFatalErrorEvent()))
                .isInstanceOf(WVFatalErrorEventException.class)
                .hasFieldOrProperty("fatalErrorEventMetadata");
    }

    @Test
    public void validationDoesNotThrowExceptionWhenKeystrokesEvent() {
        assertThatCode(() -> eventParser.validate(getKeystrokesEvent()))
                .doesNotThrowAnyException();
    }

    private Event getFatalErrorEvent() {
        return new Event(0, 0, EventType.fatalError, mock(FatalErrorEventMetadata.class));
    }

    private Event getKeystrokesEvent() {
        return new Event(0, 0, EventType.keystroke, mock(Keystrokes.class));
    }

}

class SomeEventParser implements EventParser {

    @Override
    public State2 parse(int part, EventMessageType type, byte[] data, int hid, int counterId, String url) {
        return null;
    }

    @Override
    public PackageExternal toExternal(int serialization, Package p) {
        return null;
    }

    @Override
    public Event parseAndMaskEvent(int serialization, Package p) throws IOException {
        return null;
    }

    @Override
    public PageMeta parsePageMeta(int serialization, Package p) {
        return null;
    }

    @Override
    public EventMessageType getType() {
        return null;
    }
}
