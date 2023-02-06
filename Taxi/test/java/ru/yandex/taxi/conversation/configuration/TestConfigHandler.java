package ru.yandex.taxi.conversation.configuration;

import org.apache.commons.lang.NotImplementedException;
import org.springframework.stereotype.Component;

import ru.yandex.taxi.conversation.endpoint.MailEndpoint;
import ru.yandex.taxi.conversation.envelope.mail.MailEnvelope;
import ru.yandex.taxi.conversation.handle.HandleContext;
import ru.yandex.taxi.conversation.handle.Handler;
import ru.yandex.taxi.conversation.receive.mail.IncomeMailMessage;


@Component
public class TestConfigHandler implements Handler<MailEndpoint, IncomeMailMessage, MailEnvelope> {
    @Override
    public String getId() {
        return TestConfigHandler.class.getSimpleName();
    }

    @Override
    public boolean isApplicable(IncomeMailMessage payload) {
        return true;
    }

    @Override
    public void handle(IncomeMailMessage payload, HandleContext<MailEndpoint, MailEnvelope> context) {
        throw new NotImplementedException();
    }
}

