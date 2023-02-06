package ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.exec.DwarfProcessExecuter;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.Demangler;

public class DemangleCheckTest {

    private Demangler demangler;

    @Before
    public void before() {
        DwarfProcessExecuter processExecuter = new DwarfProcessExecuter();
        processExecuter.init();
        demangler = new Demangler(processExecuter);
    }

    @Test
    public void mangled() {
        Assert.assertTrue(demangler.isMangled("_ZNK11MyException4whatEv"));
    }

    @Test
    public void mangled2() {
        Assert.assertTrue(demangler.isMangled("_ZdlPv.island"));
    }

    @Test
    public void mangled3() {
        Assert.assertTrue(demangler.isMangled("_ZNK11MyExce ption4whatEv"));
    }

    @Test
    public void nonMangled3() {
        Assert.assertFalse(demangler.isMangled("_ZNK11MyExce\nption4whatEv"));
    }

    @Test
    public void swiftMangled() {
        Assert.assertTrue(demangler.isMangled("$s5Maple11AppDelegateC11application_29didFinishLaunchingWithOptionsSbSo13UIApplicationC_SDySo0j6LaunchI3KeyaypGSgtF"));
    }

    @Test
    public void mangledItanium() {
        Assert.assertTrue(demangler.isMangled("_ZdlPv$shim"));
    }
}
