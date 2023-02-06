package ru.yandex.metrika.mobmet.crash.decoder.test.dwarf;

import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.util.DefaultIndenter;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.devtools.test.CanonicalFile;
import ru.yandex.devtools.test.Canonizer;
import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.exec.DwarfProcessExecuter;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.Demangler;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionLinesBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionTableBuilder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionsYDBService;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.model.YDBFunction;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.FilesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.InlinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.LinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.YDBFunctionSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.DwarfDebugData;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.DwarfProcessor;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.ProgramsPaths;
import ru.yandex.metrika.util.schema.CamelCaseToUnderscoreSchemaStrategy;

import static ru.yandex.devtools.test.Paths.getTestOutputsRoot;

@RunWith(Parameterized.class)
public class DwarfProcessingTest {

    @Parameterized.Parameter
    public String dwarfName;

    /**
     * Сейчас обработка всех этих параметров занимает около 5-ти минут.
     * Кажется, что после перехода на новый парсинг время сильно сократится.
     */
    @Parameterized.Parameters
    public static Collection<Object[]> initParams() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{"libedit.3.dylib_12.3.1(16F203)"})
                .add(new Object[]{"libxpc.dylib_7.1.2(11D257)"})
                .add(new Object[]{"libsqlite3.dylib_12.3.1(16F203)"})
                .add(new Object[]{"UIKit_12.3.1(16F203)"})
                .add(new Object[]{"Translate_2019.5.1(4801)"})
                .add(new Object[]{"Kinopoisk_4.8.2(7984)"})
                .add(new Object[]{"YandexDisk_279(18063)"})
                .add(new Object[]{"Music_462(28518)"})
                .build();
    }

    private DwarfProcessor processor;
    private FunctionsYDBService functionsService;

    @BeforeClass
    public static void init() {
        MediumTestsLogSetup.setup();
    }

    @Before
    public void before() {
        DwarfProcessExecuter processExecuter = new DwarfProcessExecuter();
        processExecuter.init();
        Demangler demangler = new Demangler(processExecuter);
        demangler.setItaniumDemanglerPath(ProgramsPaths.llvmCxxFiltPath());
        demangler.setSwiftDemanglerPath(ProgramsPaths.swiftDemanglePath());
        demangler.setTimeoutInSeconds(120);
        FunctionTableBuilder tableBuilder = new FunctionTableBuilder(demangler);
        FunctionLinesBuilder linesBuilder = new FunctionLinesBuilder();
        processor = new DwarfProcessor(processExecuter, tableBuilder, linesBuilder);
        processor.setSymbolsCutterPath(ProgramsPaths.symbolsCutter());
        processor.init();

        YDBFunctionSerializer serializer = new YDBFunctionSerializer(
                new FilesSerializer(), new InlinesSerializer(), new LinesSerializer());
        functionsService = new FunctionsYDBService(null, serializer);
    }

    @Test
    public void test() throws Exception {
        Path dwarfPath = Paths.get("dwarf_test_data", dwarfName);
        byte[] data = Files.readAllBytes(dwarfPath);

        List<DwarfTestData> testDataList = new ArrayList<>();
        List<DwarfDebugData> dwarfDebugData = processor.process(new ByteArrayInputStream(data));
        for (DwarfDebugData debugData : dwarfDebugData) {
            List<YDBFunction> functions = functionsService.getYDBFunctions(debugData);
            DwarfTestData testData = new DwarfTestData(debugData.getInfo(), functions);
            testDataList.add(testData);
        }

        Path output = Path.of(getTestOutputsRoot(), dwarfName + ".json");
        // записываем в файл, иначе при локальном запуске можем получить OOM
        defaultCanonizeMapper().writeValue(output.toFile(), testDataList);

        Canonizer.canonize(new CanonicalFile(output.toString()));
    }

    /**
     * Используем jackson, а не дефолтную сериализацию через Gson, чтобы лучше управлять внешним видом
     * результата
     */
    private static ObjectMapper defaultCanonizeMapper() {
        DefaultPrettyPrinter prettyPrinter = new DefaultPrettyPrinter();
        prettyPrinter.indentArraysWith(DefaultIndenter.SYSTEM_LINEFEED_INSTANCE);
        return new ObjectMapper()
                .setSerializationInclusion(JsonInclude.Include.NON_EMPTY)
                .setPropertyNamingStrategy(CamelCaseToUnderscoreSchemaStrategy.INSTANCE)
                .setDefaultPrettyPrinter(prettyPrinter)
                .enable(SerializationFeature.INDENT_OUTPUT);
    }
}
