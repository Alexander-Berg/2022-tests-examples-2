package ru.yandex.taxi.conversation.configuration;

import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

import ru.yandex.taxi.conversation.config.ConfigDataService;
import ru.yandex.taxi.conversation.config.ConfigDirectoryNotFoundException;
import ru.yandex.taxi.conversation.config.ConfigProvider;
import ru.yandex.taxi.conversation.config.DuplicateEndpointException;
import ru.yandex.taxi.conversation.config.DuplicateHandlerException;
import ru.yandex.taxi.conversation.config.DuplicateProjectException;
import ru.yandex.taxi.conversation.config.DuplicateRouteException;
import ru.yandex.taxi.conversation.config.InvalidHandlerException;
import ru.yandex.taxi.conversation.endpoint.ChatEndpointInitializer;
import ru.yandex.taxi.conversation.endpoint.EndpointInitializer;
import ru.yandex.taxi.conversation.endpoint.EndpointYamlConfigProvider;
import ru.yandex.taxi.conversation.endpoint.LogbrokerEndpointInitializer;
import ru.yandex.taxi.conversation.endpoint.MailEndpointInitializer;
import ru.yandex.taxi.conversation.endpoint.TelephonyEndpointInitializer;
import ru.yandex.taxi.conversation.handle.Handler;
import ru.yandex.taxi.conversation.project.ProjectYamlConfigProvider;
import ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration;

import static org.junit.jupiter.api.Assertions.assertThrows;


@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class InvalidConfigurationTest {

    private List<EndpointInitializer> endpointInitializers;
    private List<Handler<?, ?, ?>> handlers;

    private ObjectMapper yamlObjectMapper;


    @BeforeAll
    public void SetUp() {
        this.yamlObjectMapper = new ObjectMapperConfiguration().getYamlObjectMapper();

        Handler<?, ?, ?> testHandler = new TestConfigHandler();
        Handler<?, ?, ?> testHandler2 = new Test2ConfigHandler();

        this.handlers = List.of(testHandler, testHandler2);
        this.endpointInitializers = List.of(new ChatEndpointInitializer(), new MailEndpointInitializer(),
                new LogbrokerEndpointInitializer(), new TelephonyEndpointInitializer());
    }

    @Test
    public void EmptyConfiguration() {
        List<ConfigProvider<?>> providers = getProviders("data/emptyConfigTest/endpoint",
                "data/emptyConfigTest/project");

        assertThrows(ConfigDirectoryNotFoundException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void ClasspathEmptyConfiguration() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/emptyConfigTest/endpoint",
                "classpath:data/emptyConfigTest/project");

        assertThrows(ConfigDirectoryNotFoundException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void TwoEqualsHandlersInRoute() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/twoEqualsHandlersInRoute/endpoint",
                "classpath:data/twoEqualsHandlersInRoute/project");

        assertThrows(DuplicateHandlerException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void TwoEqualsRoutes() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/twoEqualsRoutes/endpoint",
                "classpath:data/twoEqualsRoutes/project");

        assertThrows(DuplicateRouteException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void TwoEqualsEndpoints() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/twoEqualsEndpoints/endpoint",
                "classpath:data/twoEqualsEndpoints/project");

        assertThrows(DuplicateEndpointException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void TwoEqualsProjects() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/twoEqualsProjects/endpoint",
                "classpath:data/twoEqualsProjects/project");

        assertThrows(DuplicateProjectException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    @Test
    public void InvalidHandlerInRoute() {
        List<ConfigProvider<?>> providers = getProviders("classpath:data/invalidHandlerInRoute/endpoint",
                "classpath:data/invalidHandlerInRoute/project");

        assertThrows(InvalidHandlerException.class, () -> {
            new ConfigDataService(providers, endpointInitializers, handlers);
        });
    }

    private List<ConfigProvider<?>> getProviders(String endpoint, String project) {
        ConfigProvider<?> endpointProvider = new EndpointYamlConfigProvider(endpoint, yamlObjectMapper);
        ConfigProvider<?> projectProvider = new ProjectYamlConfigProvider(project, yamlObjectMapper);

        return List.of(endpointProvider, projectProvider);
    }

}
