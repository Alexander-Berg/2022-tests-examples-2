package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.management.client.MessengerService;
import ru.yandex.metrika.api.management.client.utils.MessengerValidator;

@Configuration
@Import(MessengerServiceConfig.class)
public class MessengerValidatorConfig {

    @Bean
    public MessengerValidator messengerValidator(MessengerService messengerService) {
        return new MessengerValidator(messengerService);
    }
}
