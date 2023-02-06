package ru.yandex.taxi.conversation.configuration;


import java.util.List;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.config.ConfigDataService;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.endpoint.EndpointService;
import ru.yandex.taxi.conversation.project.RouteRule;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;


@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@SpringBootTest(classes = {SpringApplicationConfig.class})
@TestPropertySource(locations = "classpath:data/configuration/config.properties")
@SpringBootApplication(scanBasePackages = "ru.yandex.taxi.conversation.configuration")
public class ConfigDataServiceTest extends AbstractFunctionalTest {

    private final String MAIL_IN = "mail::mailInTest1";
    private final String MAIL_OUT = "mail::mailOutTest1";
    private final String LOGBROKER_IN = "logbroker::conversation-in-mail";
    private final String LOGBROKER_OUT = "logbroker::conversation-out-mail";

    @Autowired
    private ConfigDataService configDataService;

    @Autowired
    private EndpointService endpointService;

    private Endpoint mailIn;
    private Endpoint mailOut;
    private Endpoint logbrokerIn;
    private Endpoint logbrokerOut;

    @BeforeAll
    public void SetUp() {
        mailIn = configDataService.getEndpoint(MAIL_IN);
        mailOut = configDataService.getEndpoint(MAIL_OUT);
        logbrokerIn = configDataService.getEndpoint(LOGBROKER_IN);
        logbrokerOut = configDataService.getEndpoint(LOGBROKER_OUT);
    }


    @Test
    public void CheckAllConfigurations() {
        assertNotNull(mailIn);
        assertNotNull(mailOut);
        assertNotNull(logbrokerIn);
        assertNotNull(logbrokerOut);
        assertEquals(3, configDataService.getProjects().size());
        assertEquals(9, configDataService.getEndpoints().size());
    }

    @Test
    public void SomeHandlers() {
        List<RouteRule<Endpoint, Endpoint, Object, Object>> routes = endpointService.getRoutes(mailIn, logbrokerIn);
        assertEquals(1, routes.size());
        assertEquals(2, routes.get(0).getHandlers().size());
    }

    @Test
    public void OneHandlers() {
        List<RouteRule<Endpoint, Endpoint, Object, Object>> routes = endpointService.getRoutes(logbrokerOut, mailOut);
        assertEquals(1, routes.size());
        assertEquals(1, routes.get(0).getHandlers().size());
    }

    @Test
    public void SourceEqualsTarget() {
        List<RouteRule<Endpoint, Endpoint, Object, Object>> routes = endpointService.getRoutes(mailIn, mailIn);
        assertEquals(2, routes.size());

        RouteRule<Endpoint, Endpoint, Object, Object> logbrokerInRouteRule =
                routes.stream().filter(x -> x.getTo().equals(logbrokerIn)).findFirst().orElse(null);
        assertNotNull(logbrokerInRouteRule);
        assertEquals(2, logbrokerInRouteRule.getHandlers().size());

        RouteRule<Endpoint, Endpoint, Object, Object> mailOutRouteRule =
                routes.stream().filter(x -> x.getTo().equals(mailOut)).findFirst().orElse(null);

        assertNotNull(mailOutRouteRule);
        assertEquals(1, mailOutRouteRule.getHandlers().size());
    }
}

