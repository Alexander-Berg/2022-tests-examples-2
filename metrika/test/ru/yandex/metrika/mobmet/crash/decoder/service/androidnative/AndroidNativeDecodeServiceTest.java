package ru.yandex.metrika.mobmet.crash.decoder.service.androidnative;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.util.Collection;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.skyscreamer.jsonassert.JSONAssert;

import ru.yandex.metrika.mobmet.crash.android.model.androidnative.AndroidNativeCrashReport;
import ru.yandex.metrika.mobmet.crash.breakpad.Minidump;
import ru.yandex.metrika.mobmet.crash.breakpad.MinidumpStackwalk;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.InternalModelDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.model.ObjectFile;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.parser.SymbolsCutterParser;
import ru.yandex.metrika.util.io.IOUtils;

import static java.util.Collections.emptyList;

/**
 * Для запуска из IDEA используй конфиг mobile / AndroidNativeDecodeServiceTest
 * В нём выставляется необходимый java.library.path
 */
@RunWith(Parameterized.class)
public class AndroidNativeDecodeServiceTest {

    private static final int RANDOM_APP_ID = 12345;

    private static final ObjectMapper objectMapper = new ObjectMapper()
            .setSerializationInclusion(JsonInclude.Include.NON_NULL);

    @Parameterized.Parameter
    public List<ObjectFile> symbols;

    @Parameterized.Parameter(1)
    public String crashDumpPath;

    @Parameterized.Parameter(2)
    public String crashDumpDecodedPath;

    @Parameterized.Parameters(name = "crash: {1}")
    public static Collection<Object[]> createParameters() throws Exception {
        return List.of(
                // Обычный крэш
                new Object[]{
                        parseUploadedSymbols("testdata/libnative-lib.ysym"),
                        "testdata/crash.dmp",
                        "testdata/crash-decoded-expected.json"},
                // Крэш-дамп, в котором есть два разных модуля с одинаковым адресом в RAM
                new Object[]{
                        emptyList(),
                        "testdata/duplicated_address_modules.dmp",
                        "testdata/duplicated_address_modules-decoded-expected.json"}
        );
    }

    @Test
    public void decode() throws Exception {
        Minidump minidump = parseCrash(crashDumpPath);
        InternalModelDecoder decoder = MockedBeans.mockInternalModelDecoder(RANDOM_APP_ID, symbols);

        AndroidNativeMinidumpAdapterService minidumpAdapterService = new AndroidNativeMinidumpAdapterService();
        AndroidNativeCrashSymbolicationService symbolicationService = new AndroidNativeCrashSymbolicationService(decoder);

        AndroidNativeCrashReport crashReport = minidumpAdapterService.adapt(minidump);
        SymbolicationResult symbolicationResult = symbolicationService.symbolicate(crashReport, RANDOM_APP_ID);
        AndroidNativeCrashReport decodedCrashReport = symbolicationResult.getCrashReport();

        String actualCrash = objectMapper.writerFor(AndroidNativeCrashReport.class).writeValueAsString(decodedCrashReport);
        String expectedCrash = IOUtils.resourceAsString(AndroidNativeDecodeServiceTest.class, crashDumpDecodedPath);

        JSONAssert.assertEquals(expectedCrash, actualCrash, true);
    }

    private static Minidump parseCrash(String path) throws IOException {
        InputStream crashIS = AndroidNativeDecodeServiceTest.class.getResourceAsStream(path);
        byte[] crashData = crashIS.readAllBytes();
        return MinidumpStackwalk.parse(crashData);
    }

    private static List<ObjectFile> parseUploadedSymbols(String path) throws IOException {
        String symbolsData = IOUtils.resourceAsString(AndroidNativeDecodeServiceTest.class, path);
        BufferedReader reader = new BufferedReader(new StringReader(symbolsData));
        SymbolsCutterParser parser = new SymbolsCutterParser(SymbolsCutterParser.SymbolsCutterFormat.ANDROID_NATIVE);
        return parser.parse(reader);
    }
}
