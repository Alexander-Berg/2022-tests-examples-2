package ru.yandex.metrika.clickhouse.b2b;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import freemarker.ext.beans.BeansWrapper;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.*;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.metrika.clickhouse.properties.ClickhouseB2BTestsProperties;
import ru.yandex.metrika.clickhouse.steps.Sample;
import ru.yandex.metrika.clickhouse.steps.SuiteBriefResult;
import ru.yandex.metrika.clickhouse.steps.TestCase;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.ArrayList;

import static com.google.common.base.Throwables.throwIfUnchecked;
import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.DynamicContainer.dynamicContainer;

public class ClickhouseB2BTest {

    private static final Logger LOG = LogManager.getLogger(ClickhouseB2BTest.class);

    private SuiteBriefResult suiteBriefResult;

    @BeforeEach
    public void initResults() {
        suiteBriefResult = new SuiteBriefResult();
        suiteBriefResult.start();
    }

    @AfterEach
    public void writeAggregatedReport() {
        suiteBriefResult.finish();
        suiteBriefResult.sort();

        Path dst = Paths.get(ClickhouseB2BTestsProperties.getInstance().getTargetDir()).resolve("index.html");
        Configuration configuration = new Configuration();
        configuration.setTemplateExceptionHandler(TemplateExceptionHandler.HTML_DEBUG_HANDLER);
        configuration.setClassForTemplateLoading(this.getClass(), "/");
        configuration.setOutputEncoding("UTF-8");
        configuration.setDefaultEncoding("UTF-8");
        try {
            Template template = configuration.getTemplate("TestSuite.html.ftl");
            Map<String, Object> root = ImmutableMap.<String, Object>builder()
                    .put("suite", suiteBriefResult)
                    .put("ResultKind", BeansWrapper.getDefaultInstance().getEnumModels().get("ru.yandex.metrika.clickhouse.steps.DifferenceDescriptor$ResultKind"))
                    .build();
            template.process(root, new OutputStreamWriter(new FileOutputStream(dst.toFile()), StandardCharsets.UTF_8));
        } catch (TemplateException | IOException e) {
            throw new RuntimeException("Error while processing template.", e);
        }
    }

    @TestFactory
    public Iterable<DynamicNode> createTests() {
        ClickhouseB2BTestsProperties properties = ClickhouseB2BTestsProperties.getInstance();
        Path rootDir = Paths.get(properties.getRequestsBaseDir()).toAbsolutePath();

        LOG.info(String.format("requests root dir: %s", rootDir));

        // первый уровень - каталоги по демонам
        ImmutableList.Builder<DynamicNode> builder = ImmutableList.builder();
        ArrayList<String> daemons = new ArrayList<>();
        if (properties.getFacedApiTest() != null && properties.getFacedApiRef() != null) {
            daemons.add("faced");
        }
        if (properties.getMobmetdApiTest() != null && properties.getMobmetdApiRef() != null) {
            daemons.add("mobmetd");
        }
        for (String daemon : daemons) {
            builder.add(dynamicContainer(daemon, processRootDir(rootDir.resolve(daemon).toAbsolutePath(), daemon)));
        }
        return builder.build();
    }

    private Iterable<DynamicTest> processRootDir(Path rootDir, String destination) {
        if (!Files.exists(rootDir)) {
            return new ArrayList();
        }
        //Каждый тест - одна ручка.
        try {
            try (Stream<Path> paths = Files.walk(rootDir)) {
                return paths
                        .filter(p -> p.toFile().isDirectory() && p.resolve("handle").toFile().exists())
                        .filter(p -> ifProcessDir(destination, p))
                        .map(p -> processDir(p, destination,
                                ClickhouseB2BTestsProperties.getInstance().getRelativeLimit(),
                                ClickhouseB2BTestsProperties.getInstance().getAbsoluteLimit()))
                        .collect(toList());
            }
        } catch (IOException e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }

    private static boolean ifProcessDir(String destination, Path dir) {

        try {
            LOG.info(String.format("Checking: %s", dir));
            final String handle = Files.lines(dir.resolve("handle")).findFirst().get();
            boolean createTest = true;
            switch (destination) {
                case "faced":
                    createTest = shouldProcess(handle, ClickhouseB2BTestsProperties.getInstance().getFacedHandlesInclude(), ClickhouseB2BTestsProperties.getInstance().getFacedHandlesExclude());
                    break;
                case "mobmetd":
                    createTest = shouldProcess(handle, ClickhouseB2BTestsProperties.getInstance().getMobmetdHandlesInclude(), ClickhouseB2BTestsProperties.getInstance().getMobmetdHandlesExclude());
                    break;
                default:
                    throw new RuntimeException("Unsupported destination: " + destination);
            }
            if (!createTest) {
                LOG.info("Skip due to includes/excludes");
            }
            return createTest;
        } catch (IOException e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }

    private static boolean shouldProcess(String handle, String include, String exclude) {
        boolean shouldInclude = StringUtils.isEmpty(include) ? true : Pattern.matches(include, handle);
        boolean shouldExclude = StringUtils.isEmpty(exclude) ? false : Pattern.matches(exclude, handle);

        return shouldInclude && !shouldExclude;
    }

    private DynamicTest processDir(Path dir, String destination, double relativeLimit, int absoluteLimit) {

        LOG.info(String.format("Processing %s", dir));

        ImmutableList.Builder<Sample> builder = ImmutableList.builder();

        try {
            final String handle = Files.lines(dir.resolve("handle")).findFirst().get();
            final int total = Integer.valueOf(Files.lines(dir.resolve("total")).findFirst().get());
            final int uniq = Integer.valueOf(Files.lines(dir.resolve("uniq")).findFirst().get());

            AtomicInteger current_sum = new AtomicInteger(0);
            AtomicInteger final_sum = new AtomicInteger(0);
            AtomicInteger current_uniq = new AtomicInteger(0);
            AtomicReference<Double> finalPortion = new AtomicReference<>((double) 0);

            Streams.zip(Files.lines(dir.resolve("params")), Files.lines(dir.resolve("counters")),
                    (r, c) -> ImmutablePair.of(r, Integer.valueOf(c)))
                    .forEachOrdered(h -> {
                        current_sum.addAndGet(h.getValue());
                        int seq = current_uniq.incrementAndGet();
                        double currentPortion = current_sum.doubleValue() / total;
                        if (uniq <= absoluteLimit || (current_uniq.intValue() <= absoluteLimit && currentPortion < relativeLimit)) {
                            finalPortion.set(currentPortion);
                            final_sum.set(current_sum.get());
                            //FIXME тут нужно как-то без if'ов и switch'ей сделать по нормальному, когда нужно будет расширить

                            final FreeFormParameters dynamicParams = FreeFormParameters.makeParameters()
                                    .append("pretty", "true")
                                    .append("accuracy", "1");
                            final FreeFormParameters headers = FreeFormParameters.makeParameters();
                            final URL refHost;
                            final URL testHost;
                            switch (destination) {
                                case "faced":
                                    headers.append("Authorization", "OAuth " + ClickhouseB2BTestsProperties.getInstance().getFacedOauthToken());
                                    refHost = ClickhouseB2BTestsProperties.getInstance().getFacedApiRef();
                                    testHost = ClickhouseB2BTestsProperties.getInstance().getFacedApiTest();
                                    break;
                                case "mobmetd":
                                    headers.append("Authorization", "OAuth " + ClickhouseB2BTestsProperties.getInstance().getMobmetdOauthToken());
                                    refHost = ClickhouseB2BTestsProperties.getInstance().getMobmetdApiRef();
                                    testHost = ClickhouseB2BTestsProperties.getInstance().getMobmetdApiTest();
                                    break;
                                default:
                                    throw new RuntimeException("Unsupported destination: " + destination);
                            }

                            //TODO 4 варианта дат - совпадают, не пересекаются, пересекаются...
                            if (handle.contains("comparison")) {

                                dynamicParams
                                        .append("date1_a", ClickhouseB2BTestsProperties.getInstance().getStartDate())
                                        .append("date2_a", ClickhouseB2BTestsProperties.getInstance().getFinishDate())
                                        .append("date1_b", ClickhouseB2BTestsProperties.getInstance().getStartDate())
                                        .append("date2_b", ClickhouseB2BTestsProperties.getInstance().getFinishDate());
                            } else if(handle.contains("/analytics/v3/data/ga")) {
                                dynamicParams
                                        .append("start-date", ClickhouseB2BTestsProperties.getInstance().getStartDate())
                                        .append("end-date", ClickhouseB2BTestsProperties.getInstance().getFinishDate())
                                        .append("samplingLevel", "FULL");
                            }
                            else {
                                //1 вариант дат
                                dynamicParams
                                        .append("date1", ClickhouseB2BTestsProperties.getInstance().getStartDate())
                                        .append("date2", ClickhouseB2BTestsProperties.getInstance().getFinishDate());
                            }
                            builder.add(
                                    Sample.builder()
                                            .withCounter(h.getValue())
                                            .withHandle(handle)
                                            .withId(UUID.randomUUID().toString())
                                            .withParams(h.getKey())
                                            .withSeq(seq)
                                            .withRefHost(refHost)
                                            .withTestHost(testHost)
                                            .withDynamicParams(dynamicParams)
                                            .withHeaders(headers)
                                            .build()
                            );
                        }
                    });
            ImmutableList<Sample> samples = builder.build();
            LOG.info(String.format("%d requests found (%f percentile)", samples.size(), finalPortion.get()));
            return DynamicTest.dynamicTest(String.format("%s:%s", destination, handle),
                    new TestCase(suiteBriefResult, samples, destination, handle, finalPortion.get()));
        } catch (IOException e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }
}
