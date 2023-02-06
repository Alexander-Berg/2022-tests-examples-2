package ru.yandex.metrika.faced.tests.recommendations;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Random;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.Assert;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import ru.yandex.metrika.api.management.client.recommendations.RecommendationActionKind;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationDistributionType;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationInterfaceSection;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationMeta;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationReadFor;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.faced.config.RecommendationsAdminConfig;
import ru.yandex.metrika.faced.steps.RecommendationSteps;
import ru.yandex.metrika.spring.MetrikaApiMessageConverter;

@ContextConfiguration(classes = RecommendationsAdminConfig.class)
@WebAppConfiguration
public abstract class RecommendationsAdminTestBase {
    private final static int RANDOM_STRING_LENGTH = 10;
    private final static int RANDOM_INT_BOUND = 100;
    @Autowired
    protected WebApplicationContext wac;

    protected RecommendationSteps recommendationSteps;

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    protected MockMvc mockMvc;

    @Before
    public void before() {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .build();
        recommendationSteps = new RecommendationSteps(wac.getBean(MetrikaApiMessageConverter.class).getObjectMapper());

    }

    protected void checkForEqualityWithoutId(RecommendationMeta responseMeta, RecommendationMeta meta) {
        Assert.assertEquals(meta.getShowForTypes() == null ? Collections.emptySet() : meta.getShowForTypes(), responseMeta.getShowForTypes());
        Assert.assertEquals(meta.getDistributionTypes() == null ? Collections.emptySet() : meta.getDistributionTypes(), responseMeta.getDistributionTypes());
    }

    protected static RecommendationMeta getDefaultMeta() {
        Random random = new Random();
        return new RecommendationMeta(
                0,
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                random.nextInt(RANDOM_INT_BOUND) + 1,
                random.nextInt(RANDOM_INT_BOUND),
                random.nextInt(RANDOM_INT_BOUND) + 1,
                random.nextInt(RANDOM_INT_BOUND) + 1,
                new HashSet<>(getRandomElements(Arrays.asList(RecommendationDistributionType.values()), random)),
                new HashSet<>(getRandomElements(Arrays.asList(SubscriptionListType.values()), random)),
                random.nextInt(RANDOM_INT_BOUND) + 1,
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                getRandomElement(Arrays.asList(RecommendationReadFor.values()), random),
                getRandomElement(Arrays.asList(RecommendationActionKind.values()), random),
                RandomStringUtils.randomAscii(RANDOM_STRING_LENGTH),
                new HashSet<>(getRandomElements(Arrays.asList(RecommendationInterfaceSection.values()), random))
        );
    }

    private static <T> List<T> getRandomElements(Collection<T> collection, Random random) {
        List<T> copy = new ArrayList<>(collection);
        Collections.shuffle(copy);
        int n = random.nextInt(copy.size());
        return copy.subList(0, n);
    }

    private static <T> T getRandomElement(List<T> list, Random random) {
        return list.get(random.nextInt(list.size()));
    }
}
