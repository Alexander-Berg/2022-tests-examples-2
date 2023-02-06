package ru.yandex.autotests.morda.yasm;

import org.apache.log4j.Logger;
import org.junit.Test;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.qatools.monitoring.yasm.YasmData;
import ru.yandex.qatools.monitoring.yasm.YasmNotifier;
import ru.yandex.qatools.monitoring.yasm.YasmTags;
import ru.yandex.qatools.monitoring.yasm.YasmValue;

import java.util.Random;

import static java.lang.Thread.sleep;

/**
 * Created by eoff on 27.01.17.
 */
@Aqua.Test(title = "Genre")
public class SampleYasmTest {
    @Test
    public void testSend() throws InterruptedException {
        YasmNotifier notifier = new YasmNotifier();
        Logger logger = Logger.getLogger(this.getClass());

        for (int i = 0; i != 1000; i++) {
            logger.debug("Sending metric");
            YasmData yasmData = new YasmData()
                    .withTtl(300)
                    .withValues(
                            new YasmValue()
                                    .withVal(new Random().nextInt(5000))
                                    .withName("yasm_test_tttt")
                    )
                    .withTags(new YasmTags()
                            .withItype("mordafunc")
                    );

            notifier.send(yasmData);
            logger.debug("Finished send metric");
            sleep(100);
        }
    }
}
