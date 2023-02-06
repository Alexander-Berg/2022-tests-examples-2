package ru.yandex.metrika.cdp.api.tests.medium;

import java.lang.reflect.Field;
import java.util.Random;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.netflix.servo.util.Throwables;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.ClassRule;
import org.junit.Rule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.util.ReflectionUtils;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.api.management.client.counter.CounterCreator;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;
import ru.yandex.metrika.spring.quota.redis.QuotaServiceImpl;

public abstract class AbstractCdpApiTest {

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
        CdpApiTestSetup.globalSetup();
    }

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Autowired
    protected WebApplicationContext wac;

    @Autowired
    protected CounterCreator counterCreator;

    @Autowired
    protected CountersDao countersDao;

    @Autowired
    @Qualifier("quotaRedisConnectorMetrikaMock")
    protected RedisConnector quotaRedisConnectorMetrika;

    protected MockMvc mockMvc;

    @Before
    public void setUp() throws Exception {
        wac.getBeansOfType(QuotaServiceImpl.class).values().forEach(qs -> {
            try {
                Field connectorField = QuotaServiceImpl.class.getDeclaredField("connector");
                connectorField.setAccessible(true);
                ReflectionUtils.setField(connectorField, qs, quotaRedisConnectorMetrika);
            } catch (NoSuchFieldException e) {
                Throwables.propagate(e);
            }
        });
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .apply(SecurityMockMvcConfigurers.springSecurity())
                .build();
    }

    protected MetrikaUserDetails getCurrentUser() {
        return (MetrikaUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    protected int createCounter() {
        var mud = getCurrentUser();
        var counterFull = new CounterFull();
        counterFull.setName("Test counter " + new Random().nextInt(Integer.MAX_VALUE));
        counterFull.setSite2(new CounterMirrorE("ya.ru"));
        return counterCreator.createCounter(mud, mud, counterFull, false, false);
    }

    protected int createCounterWithGdpr()  {
        var mud = getCurrentUser();
        var counterFull = new CounterFull();
        counterFull.setName("Test counter " + new Random().nextInt(Integer.MAX_VALUE));
        counterFull.setSite2(new CounterMirrorE("ya.ru"));
        counterFull.setGdprAgreementAccepted(true);
        return counterCreator.createCounter(mud, mud, counterFull, false, false);
    }

    protected void deleteCounter(int counterId) {
        countersDao.deleteCounter(counterId);
    }

    protected ObjectMapper getObjectMapper() {
        return wac.getBean(MetrikaApiMessageConverter.class).getObjectMapper();
    }
}
