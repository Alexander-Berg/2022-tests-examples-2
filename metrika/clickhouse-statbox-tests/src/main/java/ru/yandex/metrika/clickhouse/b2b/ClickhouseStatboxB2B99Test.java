package ru.yandex.metrika.clickhouse.b2b;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.*;
import ru.yandex.metrika.clickhouse.properties.ClickhouseStatBoxB2BTestsProperties;
import ru.yandex.metrika.clickhouse.steps.TestCase;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

public class ClickhouseStatboxB2B99Test {

    private static final Logger LOG = LogManager.getLogger(ClickhouseStatboxB2B99Test.class);

    @TestFactory
    public Iterable<DynamicNode> createTests() throws IOException {
        Path rootDir = ClickhouseStatBoxB2BTestsProperties.getInstance().getQueriesBaseDir().resolve("test");

        LOG.info(String.format("Queries root dir: %s", rootDir));
        try (Stream<Path> paths = Files.walk(rootDir)) {
            return paths
                    .filter(p -> p.toFile().isFile())
                    .map(rethrowFunction(p -> processDMLQuery(p)))
                    .collect(toList());
        }
    }

    private static DynamicTest processDMLQuery(Path queryFile) throws IOException {
        return DynamicTest.dynamicTest(queryFile.getFileName().toString(),
                new TestCase(
                        ClickhouseStatBoxB2BTestsProperties.getInstance().getUriTest(),
                        ClickhouseStatBoxB2BTestsProperties.getInstance().getUriRef(),
                        new String(Files.readAllBytes(queryFile), StandardCharsets.UTF_8)));
    }
}
