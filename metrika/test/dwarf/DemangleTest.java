package ru.yandex.metrika.mobmet.crash.decoder.test.dwarf;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.exec.DwarfProcessExecuter;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.Demangler;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.ProgramsPaths;

public class DemangleTest {

    private Demangler demangler;

    @BeforeClass
    public static void init() {
        MediumTestsLogSetup.setup();
    }

    @Before
    public void before() {
        DwarfProcessExecuter processExecuter = new DwarfProcessExecuter();
        processExecuter.init();
        demangler = new Demangler(processExecuter);
        demangler.setItaniumDemanglerPath(ProgramsPaths.llvmCxxFiltPath());
        demangler.setSwiftDemanglerPath(ProgramsPaths.swiftDemanglePath());
    }

    @Test
    public void test() throws Exception {
        Map<String, String> actual = demangler.demangle(List.of(
                "_Zadfafa",
                "_ZNK11MyException4whatEv",
                "_ZNK11MyBebe4whatEv",
                "$s5Maple11AppDelegateC11application_29didFinishLaunchingWithOptionsSbSo13UIApplicationC_SDySo0j6LaunchI3KeyaypGSgtF",
                "_T04file8functionyy",
                "_ZdlPv$shim",
                "_ZdlPv.island"));

        Map<String, String> expected = new HashMap<>();
        expected.put("_Zadfafa", "operator&(float, signed char, float, signed char)");
        expected.put("_ZNK11MyException4whatEv", "MyException::what() const");
        expected.put("_ZNK11MyBebe4whatEv", "MyBebe4what() const");
        expected.put("$s5Maple11AppDelegateC11application_29didFinishLaunchingWithOptionsSbSo13UIApplicationC_SDySo0j6LaunchI3KeyaypGSgtF",
                "AppDelegate.application(_:didFinishLaunchingWithOptions:)");
        expected.put("_T04file8functionyy", "filefunction empty-list  empty-list ");
        expected.put("_ZdlPv$shim", "_ZdlPv$shim");
        expected.put("_ZdlPv.island", "operator delete(void*) (.island)");

        // TreeMap чтобы легче было понять в чём ошибка
        Assert.assertEquals(new TreeMap<>(expected), new TreeMap<>(actual));
    }

    /**
     * Этот тест видимо нужно канонизировать или удалить
     */
    @Ignore
    @Test
    public void testHugeInput() throws Exception {
        String dwarf = Files.readString(Paths.get("/home/dancingelf/syms/huge_demangler_input.txt"));
        List<String> input = List.of(dwarf.strip().split("\n"));
        Map<String, String> result = demangler.demangle(input);
        result.forEach((key, value) -> {
            System.out.println(key);
            System.out.println(value);
            System.out.println();
        });
    }

}
