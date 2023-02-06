package ru.yandex.metrika.topsites;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.ZonedDateTime;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import groovy.lang.GroovyClassLoader;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.qe.hitman.comrade.script.model.ComradeClient;
import ru.yandex.qe.hitman.comrade.script.model.operation.IncrementTaskOverlapOperation;
import ru.yandex.qe.hitman.comrade.script.model.operation.Operation;
import ru.yandex.qe.hitman.comrade.script.model.toloka.Assignment;
import ru.yandex.qe.hitman.comrade.script.model.toloka.AssignmentStatus;
import ru.yandex.qe.hitman.comrade.script.model.toloka.IncrementOverlapParams;
import ru.yandex.qe.hitman.comrade.script.model.toloka.KnownSolution;
import ru.yandex.qe.hitman.comrade.script.model.toloka.Solution;
import ru.yandex.qe.hitman.comrade.script.model.toloka.Task;

import static org.mockito.Mockito.any;
import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

@RunWith(Parameterized.class)
public class DynamicOverlapScriptTest {

    public static final String SCRIPT_PATH = "/ru/yandex/metrika/topsites/DynamicOverlapScript.groovy";

    private static Class<?> dynamicOverlapScriptClass;
    private static Method onEventMethod;

    private ComradeClient comradeClient;
    private Object dynamicOverlapScript;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {
                        "less than min overlap",
                        ImmutableList.of(
                                createAssignment("1", "news"),
                                createAssignment("2", "news")
                        ),
                        new IncrementTaskOverlapOperation(new IncrementOverlapParams("1", 15))
                },
                {
                        "reached min accuracy",
                        ImmutableList.of(
                                createAssignment("1", "news"),
                                createAssignment("2", "news"),
                                createAssignment("3", "news"),
                                createAssignment("4", "news"),
                                createAssignment("5", "music")
                        ),
                        null
                },
                {
                        "less than min accuracy",
                        ImmutableList.of(
                                createAssignment("1", "news"),
                                createAssignment("2", "news"),
                                createAssignment("3", "news"),
                                createAssignment("4", "news"),
                                createAssignment("5", "news"),
                                createAssignment("6", "news"),
                                createAssignment("7", "news"),
                                createAssignment("8", "music"),
                                createAssignment("9", "music")
                        ),
                        new IncrementTaskOverlapOperation(new IncrementOverlapParams("1", 15))
                },
                {
                        "reached min accuracy, with honeypots",
                        ImmutableList.of(
                                createAssignment("1", "news", "news"),
                                createAssignment("2", "news", "news"),
                                createAssignment("1", "news"),
                                createAssignment("2", "news"),
                                createAssignment("3", "news"),
                                createAssignment("4", "news"),
                                createAssignment("5", "news"),
                                createAssignment("6", "news"),
                                createAssignment("7", "news"),
                                createAssignment("8", "music"),
                                createAssignment("9", "music")
                        ),
                        null
                },
                {
                        "reached max overlap",
                        ImmutableList.of(
                                createAssignment("1", "news"),
                                createAssignment("2", "news"),
                                createAssignment("3", "news"),
                                createAssignment("4", "news"),
                                createAssignment("5", "news"),
                                createAssignment("6", "music"),
                                createAssignment("7", "music"),
                                createAssignment("8", "music"),
                                createAssignment("9", "music"),
                                createAssignment("10", "music")
                        ),
                        null
                },
        });
    }

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public List<Assignment> assignments;

    @Parameterized.Parameter(2)
    public Operation<?> operation;

    @BeforeClass
    public static void initClass() {
        Path scriptPath = Paths.get(SCRIPT_PATH);
        GroovyClassLoader groovyClassLoader = new GroovyClassLoader();
        try (Reader reader = new InputStreamReader(DynamicOverlapScriptTest.class.getResourceAsStream(scriptPath.toString()))) {
            dynamicOverlapScriptClass = groovyClassLoader.parseClass(reader, scriptPath.getFileName().toString());
            onEventMethod = dynamicOverlapScriptClass.getMethod("onEvent", List.class, ComradeClient.class);
        } catch (IOException | NoSuchMethodException e) {
            throw new RuntimeException(e);
        }
    }

    @Before
    public void init() {
        comradeClient = spy(new StubComradeClient(createStorage()));

        try {
            dynamicOverlapScript = dynamicOverlapScriptClass.newInstance();
        } catch (IllegalAccessException | InstantiationException e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    public void test() {
        invokeOnEvent(assignments, comradeClient);

        if (operation != null) {
            verify(comradeClient).enqueueOperation(eq(operation));
        } else {
            verify(comradeClient, never()).enqueueOperation(any());
        }
    }

    private void invokeOnEvent(List<Assignment> assignments, ComradeClient comradeClient) {
        try {
            onEventMethod.invoke(dynamicOverlapScript, assignments, comradeClient);
        } catch (IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }

    private static Map<String, Object> createStorage() {
        return ImmutableMap.of(
                "params", ImmutableMap.builder()
                        .put("moreLogging", true)
                        .put("delaySeconds", 0)
                        .put("minOverlap", 3)
                        .put("maxOverlap", 10)
                        .put("minAccuracy", 0.8d)
                        .put("skillSmoothingFactor", 10)
                        .put("skillInitialFactor", 0.2d)
                        .put("mainField", "result")
                        .put("multipleScales", false)
                        .put("possibleSolutionsScript", "" +
                                "[ " +
                                "\"analytics\", " +
                                "\"b2b\", " +
                                "\"blog\", " +
                                "\"board\", " +
                                "\"cityportal\", " +
                                "\"community\", " +
                                "\"edu\", " +
                                "\"encyclopedia\", " +
                                "\"fun\", " +
                                "\"games\", " +
                                "\"gov\", " +
                                "\"library\", " +
                                "\"meta-shop\", " +
                                "\"movie\", " +
                                "\"music\", " +
                                "\"network\", " +
                                "\"news\", " +
                                "\"nocommerce\", " +
                                "\"porno\", " +
                                "\"portal\", " +
                                "\"recipe\", " +
                                "\"service\", " +
                                "\"shop-goods\", " +
                                "\"shop-service\", " +
                                "\"torrent\", " +
                                "\"other\", " +
                                "\"error\" " +
                                "]"
                        )
                        .put("accuracyAlgorithm", "WEIGHTED_MV")
                        .build(),
                "user#1", ImmutableMap.of(
                        "right", 15,
                        "all", 30
                )
        );
    }

    private static Assignment createAssignment(String workerId, String result) {
        return createAssignment(workerId, result, null);
    }

    private static Assignment createAssignment(String workerId, String result, String knownSolution) {
        return new Assignment(
                "1", "1", "1", workerId,
                AssignmentStatus.ACCEPTED,
                BigDecimal.ONE,
                ImmutableList.of(new Task("1",
                        ImmutableMap.of("domain", "test.com", "url", "http://test.com"),
                        knownSolution != null ?
                                ImmutableList.of(new KnownSolution(ImmutableMap.of("result", knownSolution), 1d)) :
                                Collections.emptyList()
                )),
                ImmutableList.of(new Solution(ImmutableMap.of("result", result))),
                "",
                ZonedDateTime.now(), ZonedDateTime.now(), ZonedDateTime.now(),
                null, null, null
        );
    }
}
