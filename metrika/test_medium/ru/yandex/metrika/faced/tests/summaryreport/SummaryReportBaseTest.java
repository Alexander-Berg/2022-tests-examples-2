package ru.yandex.metrika.faced.tests.summaryreport;

import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;
import java.util.List;
import java.util.Random;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Hex;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.RandomUtils;
import org.apache.commons.math3.random.RandomDataGenerator;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.ClassRule;
import org.junit.Rule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers;
import org.springframework.security.web.FilterChainProxy;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.api.management.client.GrantsService;
import ru.yandex.metrika.api.management.client.counter.CounterCreator;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSubscriptionCountersProvider;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramSubscription;
import ru.yandex.metrika.api.management.client.external.summaryreport.TelegramAuthorizationData;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.faced.config.SummaryReportConfig;
import ru.yandex.metrika.faced.steps.SummaryReportSteps;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultHandlers.exportTestSecurityContext;
import static ru.yandex.metrika.faced.config.SummaryReportConfig.botToken;

@ContextConfiguration(classes = SummaryReportConfig.class)
@WebAppConfiguration
public abstract class SummaryReportBaseTest {
    protected static final int MAX_COUNTERS_PER_SUBSCRIPTION = 5;
    protected static final int BIG_USER_THRESHOLD = 4;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    private final static RandomDataGenerator dataGenerator = new RandomDataGenerator();
    private final static List<String> langs = List.of("ru", "en", "de");
    private final static String CHECK_MAC_ALGORITHM = "HmacSHA256";

    private byte[] botTokenHash;

    protected SummaryReportSteps summarySteps;

    @Autowired
    protected WebApplicationContext wac;

    @Autowired
    protected FilterChainProxy springSecurityFilterChain;

    @Autowired
    protected CounterCreator counterCreator;

    @Autowired
    protected CountersDao countersDao;

    @Autowired
    protected GrantsService grantsService;

    @Autowired
    protected SummaryReportSubscriptionCountersProvider provider;

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    protected MockMvc mockMvc;

    @Before
    public void setup() throws Exception {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .apply(SecurityMockMvcConfigurers.springSecurity(springSecurityFilterChain))
                .alwaysDo(exportTestSecurityContext())
                .build();

        provider.setMaxCountersPerSubscription(MAX_COUNTERS_PER_SUBSCRIPTION);
        provider.setBigUserCountersThreshold(BIG_USER_THRESHOLD);
        summarySteps = new SummaryReportSteps(wac.getBean(MetrikaApiMessageConverter.class).getObjectMapper());
        botTokenHash = MessageDigest.getInstance("SHA256").digest(botToken.getBytes(StandardCharsets.UTF_8));
    }

    private Mac initMac() {
        try {
            Mac hmacSHA256 = Mac.getInstance(CHECK_MAC_ALGORITHM);
            hmacSHA256.init(new SecretKeySpec(botTokenHash, CHECK_MAC_ALGORITHM));
            return hmacSHA256;
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException(e);
        }
    }

    protected static Long getRandomLong() {
        return dataGenerator.nextLong(1000, Long.MAX_VALUE);
    }

    protected static Integer getRandomInt() {
        return dataGenerator.nextInt(1000, Integer.MAX_VALUE);
    }

    protected int createCounter(MetrikaUserDetails owner) {
        CounterFull counterFull = new CounterFull();
        counterFull.setName("Test counter " + new Random().nextInt(Integer.MAX_VALUE));
        counterFull.setSite2(new CounterMirrorE("ya.ru"));
        return counterCreator.createCounter(owner, owner, counterFull, false, false);
    }

    protected void addGrant(MetrikaUserDetails grantor, MetrikaUserDetails grantee, int counterId, GrantType grantType) {
        grantsService.saveGrant(grantor.getUid(), counterId, grantType, grantee.getUid(), "", new Date());
    }

    protected void deleteCounter(int counterId) {
        countersDao.deleteCounter(counterId);
    }

    protected static TelegramAuthorizationData getBaseAuthData() {
        return new TelegramAuthorizationData(
                getRandomLong(),
                RandomStringUtils.random(10, true, false),
                null,
                RandomStringUtils.random(8, true, false),
                null,
                null,
                null
        );
    }

    protected static String getRandomLanguage() {
        return langs.get(RandomUtils.nextInt(0, langs.size()));
    }

    protected String getAuthHash(String dataCheckString) {
        return Hex.encodeHexString(initMac().doFinal(dataCheckString.getBytes(StandardCharsets.UTF_8)));
    }

    protected void checkSubscription(
            SummaryReportTelegramSubscription subscription,
            SubscriptionListType type,
            long telegramUid,
            String telegramUsername,
            String lang,
            List<Integer> telegramSubscriptions,
            long uid
    ) {
        assertEquals(type, subscription.getSubscriptionType());
        assertEquals(telegramUsername, subscription.getTelegramUsername());
        assertEquals(lang, subscription.getLang());
        assertEquals(telegramUid, subscription.getTelegramUid());
        assertEquals(uid, subscription.getUid());
        assertThat(subscription.getCounterSubscriptions(), Matchers.is(telegramSubscriptions));
    }

}
