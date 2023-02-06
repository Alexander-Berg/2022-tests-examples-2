package ru.yandex.metrika.mobile.push.api.tests;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.rules.TestName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.mobile.push.api.steps.PushApiSteps;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapter;
import ru.yandex.qatools.allure.annotations.Features;

/**
 * Добавить сюда @Transactional нельзя, потому что у нас есть тесты, которые используют awaitility
 * для проверки условий асинхронных методов. awaitility запускает условия в отдельных потоках,
 * которые не видят изменния в транзацкции
 */
@ContextConfiguration(classes = PushApiConfig.class)
@WebAppConfiguration
@Features("PushAPI")
public abstract class PushApiBaseTest {

    private static final Logger log = LoggerFactory.getLogger(PushApiBaseTest.class);

    @ClassRule
    public static final SpringClassRule SCR = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Rule
    public TestName testName = new TestName();

    @Autowired
    protected PushApiSteps steps;

    @Autowired
    protected WebApplicationContext webApplicationContext;

    protected MockMvc mockMvc;

    protected PushGroupAdapter group;

    @BeforeClass
    public static void init() {
        ConfigHelper.configure();
    }

    @Before
    public void setup() {
        log.info("Test {} start", testName.getMethodName());

        steps.prepare();

        mockMvc = MockMvcBuilders
                .webAppContextSetup(webApplicationContext)
                .apply(SecurityMockMvcConfigurers.springSecurity())
                .build();
    }

    @After
    public void teardown() {
        log.info("Test {} end", testName.getMethodName());
    }
}
