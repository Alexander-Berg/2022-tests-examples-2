package ru.yandex.metrika.lambda.steps.juggler;

import org.springframework.stereotype.Component;

import ru.yandex.metrika.util.juggler.JugglerEventBuilder;
import ru.yandex.metrika.util.juggler.JugglerProperties;

@Component("jugglerReporter")
public class JugglerReporter extends ru.yandex.metrika.util.juggler.JugglerReporter {

    public JugglerReporter() {
        super("", new JugglerProperties());
    }

    public JugglerReporter(String hostName, JugglerProperties jugglerProperties) {
        super(hostName, jugglerProperties);
    }

    @Override
    public void sendEvent(JugglerEventBuilder eventBuilder) { }

    @Override
    public void close() { }
}
