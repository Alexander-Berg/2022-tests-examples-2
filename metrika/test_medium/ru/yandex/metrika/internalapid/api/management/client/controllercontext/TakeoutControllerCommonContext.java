package ru.yandex.metrika.internalapid.api.management.client.controllercontext;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

import ru.yandex.metrika.internalapid.admin.AdminController;
import ru.yandex.metrika.internalapid.takeout.TakeoutController;
import ru.yandex.metrika.internalapid.takeout.TakeoutDeleteController;
import ru.yandex.metrika.internalapid.takeout.TakeoutService;

@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class TakeoutControllerCommonContext {

    @Bean
    public TakeoutController takeoutController() {
        return new TakeoutController();
    }

    @Bean
    public AdminController adminController() {
        return new AdminController();
    }

    @Bean
    public TakeoutDeleteController takeoutDeleteController(TakeoutService takeoutService) {
        return new TakeoutDeleteController(takeoutService);
    }
}
