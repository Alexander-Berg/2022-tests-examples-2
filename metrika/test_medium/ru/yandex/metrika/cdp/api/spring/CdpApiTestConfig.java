package ru.yandex.metrika.cdp.api.spring;

import io.lettuce.core.cluster.pubsub.api.sync.RedisClusterPubSubCommands;
import org.mockito.Mockito;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.ImportResource;
import org.springframework.context.annotation.Primary;
import org.springframework.security.core.userdetails.UserDetailsService;

import ru.yandex.metrika.api.management.client.external.goals.CdpGoals;
import ru.yandex.metrika.apiclient.intapi.MetrikaIntapiFacade;
import ru.yandex.metrika.cdp.api.users.CdpApiTestUserDetailsService;
import ru.yandex.metrika.cdp.api.users.UserCreatorBeanFactoryPostProcessor;
import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.rbac.metrika.MetrikaRbac;
import ru.yandex.metrika.util.cache.RedisConnectionMock;
import ru.yandex.metrika.util.cache.RedisConnectorMock;

import static org.mockito.Matchers.anyInt;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;


@Configuration
@ImportResource({
        "classpath:/ru/yandex/metrika/cdp/api/spring/cdp-api-test-counter-creator-config.xml",
})
@Import(CdpApiConfig.class)
public class CdpApiTestConfig {

    @Primary
    @Bean
    public UserDetailsService testUserDetailsService(MetrikaRbac metrikaRbac) {
        return new CdpApiTestUserDetailsService(metrikaRbac);
    }

    @Bean
    public static UserCreatorBeanFactoryPostProcessor userCreatorPostProcessor() {
        return new UserCreatorBeanFactoryPostProcessor();
    }

    @Primary
    @Bean("mockMetrikaIntapiFacade")
    public MetrikaIntapiFacade metrikaIntapiFacade() {
        var mocked = mock(MetrikaIntapiFacade.class);
        CdpGoals goals = new CdpGoals(100, 200);
        doReturn(goals).when(mocked).getCdpGoals(anyInt());
        return mocked;
    }

    @Primary
    @Bean("quotaRedisConnectorMetrikaMock")
    public RedisConnector quotaRedisConnectorMetrikaMock() {
        return new RedisConnectorMock(new RedisConnectionMock<String, String>(Mockito.mock(RedisClusterPubSubCommands.class)), true);
    }
}


