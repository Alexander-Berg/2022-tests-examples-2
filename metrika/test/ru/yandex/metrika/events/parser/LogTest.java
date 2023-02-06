package ru.yandex.metrika.events.parser;

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.Charset;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Joiner;
import com.google.common.io.Files;
import org.junit.Ignore;

import ru.yandex.metrika.util.Base64;
import ru.yandex.metrika.util.Patterns;

/**
 * Created by orantius on 5/30/14.
 */
@Ignore
public class LogTest {
    //static String log = "HAD9CM0E-QibBgEBRAArAAD9CNUIAAECTQENXf0AAQNkAhpCAPkHpwEGAEcAbABvAGIAYQBsAAEEYAMaAVqnAdQH3QYEAE0AYQBpAG4AAQVgBBoBkQKnAZwG3QYHAEMAbwBuAHQAZQBuAHQAAQZFBRqvArcB-gUADdUCm-8BB2AGGgKvAsYB8wWwAxcAcgB1AGIAXwBzAHQAYQBuAGQAYQByAGQAXwB0AGUAeAB0AGUALQAxADMAMgA5AAEIRQcarwLGAfMFpgOmbwJuOwEJRQgarwLGAfMF3gEAAAABCkUJLq8CxgHfBd4BAAACVDMCDgrLAWQCEArOAWUCEQrSAWoCEQreAXQCEQrzAYABAhIKhQKKAQISCpYCkwECEgqlApoBAhMKtgKiAQITCsUCqAECFArWAq8BAhQK6AK4AQIVCoIDwgECFgqyA9EBAQtBCBoBrwKkA-MFLW-dAAIXC-gDBAEMQQsaAq8CpAPzBQA59gABDUUMGqcFqQOsAbkBOfYAAhcNkAECAhkNnAEDAQ5FDQGwBa0DAACmqwJ02gEPRQ4lsAWtA6IBFaarAAIbD5gBAgIdD5oBBgIdD50BCwIfD6EBDAIfC6cEFQIgC6wEFAIgC7EEEgEQQQsaA68CpAPzBQAcKgABEUUQGuIGqQOsAbkBHCoAAiERCAkBEkURAesGrQMAABWEAsV5ARNFEiXrBq0DogEVFYQAAiETCwECIhEgAQIiC94EAgIjCuQE3QECIwrpBNoBAiQK7gTVAQIkCvUE0QECJQr6BMwBAiUKgAXHAQImCoUFwgECJgqLBbwBAicKjwW3AQInCpMFtAECKAqWBbEBAigKmAWtAQIpCpsFqgECKQqeBaUBAioKoQWhAQIqCqMFnQECKwqmBZgBAiwKqAWUAQIsCqwFkAECLQqvBYsBAi0KtgWGAQItCsAFfgIuCsoFdwIuCtMFcgIvCtsFbgIvCeQFaQIwCe4FYwIwBNMHdwIxAbwIkgICMQHHCIoCAjIBzwiDAgIyAdQI-gECMwHaCPoBAjMB3gj4AQI0AeMI9QECNAHnCPIBAjUB7AjwAQI1AfAI7QECNgH0COoBAjYB*AjoAQI3AfwI5gEcbfwIzQT8CNUIHHH5CM0E*QjVCBx1*AjNBPgI1QgKjAEB*AjVCASMAQH-CNoBAQOOAQAKA48BABQDkAEALAOQAQA8A5ABAEoDkQEAWAORAQByA5IBAH4DkwEAigEDlQEAlAEDlgEAoAEDlwEAqgEDmQEAtAEDnAEAvgEDngEAyAEDoQEA0gEDogEA3AEDowEA6AEDpAEA8gEDpgEA-AEDpwEAhgIDpwEAkAIDqgEAmgIDqwEApgIDrAEAsAIDrgEAugIDrwEAxAIDsQEAzgIDtAEA2AIDtQEA5AIDvAEA7gIDxQEA*AIDxgEAggMDyAEAjAMDygEAlgMDywEAoAMDzgEAqgMD0AEAtgMD0QEAwAMD0wEAygMD1QEA1AMD1gEA4AMD1wEA6gMD2AEA*AMD2QEAggQD8QEA7AMD8QEA0gMD8QEAxgMD8gEAtgMD8gEApAMD8gEAlAMD8wEAigMD8wEA9gID9AEA4AID9AEAxgID9AEAsgID9QEAmgID9QEAiAID9QEA-AED9gEA5gED9gEA1AED9gEAyAED9wEAtgED9wEAoAED9wEAjAED*AEAfAP4AQBqA-gBAFgD*QEAQgP5AQAkA-kBAAIe-wEB4wgvAQr-AQL4CNUIAv8BAuMILwL-AQLdCCgCgAIC1ggkAoACAscIHwmBAgNAAAEUZAMaWADhB6cBBgBIAGUAYQBkAGUAcgABFWwUGgQATABvAGcAbwACgQIV3wceAoECFcsHHAKCAhW*BxsCggIVuAcaAoMCFbUHFgKDAhW0BxIBFnAUGgHNBwBiDwUATwB0AGgAZQByfHwAARdRFgEB-wcAMA*tiK2IAtN9AoQCFwsOAoQCFwgIAoUCFwQADQ__";

    public static void main(String[] args) throws Exception {
        List<String> strings = Files.readLines(new File("/home/orantius/dev/projects/metrika/trunk_git/webvisor-common/src/test/ru/yandex/metrika/events/parser/webvisor.dump"), Charset.defaultCharset());
        PrintWriter fw = new PrintWriter(new File("/home/orantius/dev/projects/metrika/trunk_git/webvisor-common/src/test/ru/yandex/metrika/events/parser/webvisor.2.dump"));
        for (String string : strings) {
            try {
                String[] split = Patterns.TAB.split(string);
                StateFull stateFull = PacketSequenceParser.parseFull(Base64.VISOR.decodeWithPadding(split[split.length-1]));
                ObjectMapper pm = new ObjectMapper();
                split[split.length-1] = pm.writeValueAsString(stateFull.getObjects());
                fw.print(Joiner.on("\t").join(split));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        fw.close();
    }
}
