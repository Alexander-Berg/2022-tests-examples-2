package ru.yandex.metrika.clickhouse.steps;

import com.google.common.collect.ImmutableMap;
import freemarker.ext.beans.BeansWrapper;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;
import io.qameta.allure.Allure;
import io.qameta.allure.model.Link;
import io.qameta.allure.model.Parameter;
import io.qameta.allure.util.ResultsUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.function.Executable;
import ru.yandex.metrika.clickhouse.properties.ClickhouseB2BTestsProperties;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.StringWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

import static com.google.common.base.Throwables.throwIfUnchecked;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toMap;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assumptions.assumeTrue;
import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

public class TestCase implements Executable {

    private static final Logger LOG = LogManager.getLogger(TestCase.class);

    private final List<Sample> samples;
    private final String destination;
    private final String handle;
    private final double percentile;
    private final SuiteBriefResult suiteBriefResult;

    public TestCase(SuiteBriefResult suiteBriefResult, List<Sample> samples, String destination, String handle, double percentile) {
        this.suiteBriefResult = suiteBriefResult;
        LOG.info(String.format("TestCase for %s:%s created", destination, handle));
        this.samples = samples;
        this.destination = destination;
        this.handle = handle;
        this.percentile = percentile;
    }

    public List<Sample> getSamples() {
        return samples;
    }

    public String getDestination() {
        return destination;
    }

    public String getHandle() {
        return handle;
    }

    public double getPercentile() {
        return percentile;
    }

    @Override
    public void execute() throws Throwable {
        LOG.info(String.format("Start execute TestCase for %s:%s", destination, handle));
        Allure.getLifecycle().updateTestCase(testResult ->
                testResult.setName(String.format("%s:%s ", destination, handle))
                        .setParameters(
                                new Parameter().setName("Количество").setValue(String.valueOf(samples.size())),
                                new Parameter().setName("Доля").setValue(String.format("%f", percentile))));
        Allure.addDescription(String.format("Демон: %s, ручка: %s", destination, handle));

        Allure.getLifecycle().updateTestCase(testResult -> testResult.setLabels(ResultsUtils.createStoryLabel(handle), ResultsUtils.createFeatureLabel(destination)));

        TestCaseResults testCaseResults = TestCaseResults.builder()
                .withDestination(destination)
                .withHandle(handle)
                .withPercentile(percentile)
                .start()
                .withSamples(processSamples())
                .finish()
                .build();

        writeAggretatedReport(renderAggregatedReport(testCaseResults));
        addLinkToAggregatedReport();
        suiteBriefResult.add(TestCaseBriefResult.builder()
                .withDestination(testCaseResults.getDestination())
                .withHandle(testCaseResults.getHandle())
                .withPercentile(testCaseResults.getPercentile())
                .withTotalSamples(testCaseResults.getTotalSamples())
                .withAggregatedResults(Stream.of(DifferenceDescriptor.ResultKind.values()).collect(toMap(r -> r, r -> testCaseResults.getTotalSamplesByResultKind(r))))
                .withStartDateTime(testCaseResults.getStartDateTime())
                .withFinishDateTime(testCaseResults.getFinishDateTime())
                .build());
        LOG.info(String.format("Finish execute TestCase for %s:%s", destination, handle));
        analyzeAggregatedResult(testCaseResults);
    }

    private void analyzeAggregatedResult(TestCaseResults testCaseResults) {
        /*
        1. Пройтись по всем, посчитать если ли conclusive, если нет - broken
        2. Пройтись по всем, посчитать, есть ли fail, если есть - fail,
        3. Пройтись по всем, посчитать, есть ли broken, если есть - broken
        4. Дошли сюда - success
         */

        assumeTrue(testCaseResults.getSamples().stream().anyMatch(s -> s.getDiff().getResultKind().isConclusive()),
                "Значимые результаты не обнаружены");

        assertFalse(testCaseResults.getSamples().stream()
                        .filter(s -> s.getDiff().getResultKind().isConclusive())
                        .anyMatch(s -> s.getDiff().getResultKind() == DifferenceDescriptor.ResultKind.NEGATIVE ||
                                s.getDiff().getResultKind() == DifferenceDescriptor.ResultKind.NOT_SIMILAR),
                "Обнаружены значимые различия");
        if (testCaseResults.getSamples().stream()
                .anyMatch(s -> s.getDiff().getResultKind() == DifferenceDescriptor.ResultKind.UNEXPECTED ||
                        s.getDiff().getResultKind() == DifferenceDescriptor.ResultKind.BROKEN ||
                        s.getDiff().getResultKind() == DifferenceDescriptor.ResultKind.INTERNAL_TEST_ERROR)) {
            throw new RuntimeException("Обнаружены значимые поломки теста");
        }
    }

    private String renderAggregatedReport(TestCaseResults testCaseResults) {
        Configuration configuration = new Configuration();
        configuration.setTemplateExceptionHandler(TemplateExceptionHandler.HTML_DEBUG_HANDLER);
        configuration.setClassForTemplateLoading(this.getClass(), "/");
        configuration.setOutputEncoding("UTF-8");
        configuration.setDefaultEncoding("UTF-8");
        try {
            Template template = configuration.getTemplate("TestCase.html.ftl");
            Map<String, Object> root = ImmutableMap.<String, Object>builder()
                    .put("testCase", testCaseResults)
                    .put("ResultKind", BeansWrapper.getDefaultInstance().getEnumModels().get("ru.yandex.metrika.clickhouse.steps.DifferenceDescriptor$ResultKind"))
                    .build();

            StringWriter stringWriter = new StringWriter();
            template.process(root, stringWriter);

            return stringWriter.toString();
        } catch (TemplateException | IOException e) {
            throw new RuntimeException("Error while processing template.", e);
        }
    }

    private void writeAggretatedReport(String report) {
        Path dst = getTestCaseReportDestination();
        dst.getParent().toFile().mkdirs();
        try (OutputStreamWriter writer = new OutputStreamWriter(new FileOutputStream(dst.toFile()), "utf-8")) {
            writer.write(report);
        } catch (Exception e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }

    private void addLinkToAggregatedReport() {
        Allure.addLinks(new Link()
                .setName("B2B-отчёт сравнения ответов")
                .setUrl("../" +
                        Paths.get(ClickhouseB2BTestsProperties.getInstance().getTargetDir()).getFileName().toString() +
                        "/" +
                        getTestCaseReportFileName()));
    }

    private List<SampleResult> processSamples() throws InterruptedException {
        LOG.info("processSamples");
        //начинаем паралелльную обработку
        ExecutorService executorService = Executors.newFixedThreadPool(ClickhouseB2BTestsProperties.getInstance().getForkPoolSize());
        List<Future<SampleResult>> futures = executorService.invokeAll(samples.stream().map(s -> new SampleTask(s, getSamplesReportDestination())).collect(toList()));
        LOG.info("Start waiting results");
        while (futures.stream().anyMatch(f -> !f.isDone())) {
            long done = futures.stream().filter(f -> f.isDone()).count();
            LOG.info(String.format("Progress: %d of %d (%.0f%%)", done, futures.size(), ((float) 100 * done) / futures.size()));
            TimeUnit.MINUTES.sleep(1);
        }
        LOG.info("All futures are done. Getting results.");
        List<SampleResult> results = futures.stream().map(rethrowFunction(f -> f.get())).collect(toList());
        LOG.info("All results done.");
        //параллельная обработка завершена, уничтожаем пул
        executorService.shutdownNow();
        LOG.info("after shutdown");
        executorService.awaitTermination(30L, TimeUnit.SECONDS);
        LOG.info("after awaitTermination");

        return results;
    }

    private Path getSamplesReportDestination() {
        return Paths.get(ClickhouseB2BTestsProperties.getInstance().getTargetDir(),
                String.format("%s/%s", destination, handle));
    }

    private Path getTestCaseReportDestination() {
        return Paths.get(ClickhouseB2BTestsProperties.getInstance().getTargetDir()).resolve(
                getTestCaseReportFileName());
    }

    private String getTestCaseReportFileName() {
        return String.format("%s/%s/index.html", destination, handle);
    }
}
