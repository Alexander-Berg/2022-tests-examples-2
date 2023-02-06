package ru.yandex.metrika.mobmet.crash.decoder.test.daemon.spring;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.google.common.collect.ImmutableMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.mobmet.crash.decoder.steps.MobmetCrashDecoderSettings;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.ProgramsPaths;
import ru.yandex.metrika.mobmet.crash.decoder.test.daemon.MobmetCrashDecoderProcessingTest;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;
import static ru.yandex.devtools.test.Paths.getBuildPath;
import static ru.yandex.metrika.common.test.medium.FreemarkerUtils.renderTemplate;

public final class ConfigHelper {

    private static final Logger log = LoggerFactory.getLogger(ConfigHelper.class);

    private ConfigHelper() {
    }

    public static void configure() {
        final String configFile = getBuildPath("config.xml");
        ImmutableMap.Builder<String, String> overrideEnvBuilder = ImmutableMap.builder();
        overrideEnvBuilder.put("targetHost", "localhost");

        log.info("Writing configuration file: {}", configFile);
        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(configFile))) {
            MobmetCrashDecoderSettings settings = new MobmetCrashDecoderSettings();
            writer.write(renderTemplate("/ru/yandex/metrika/mobmet/crash/decoder", "test/daemon/spring/config.conf.ftl",
                    ImmutableMap.<String, String>builder()
                            .putAll(System.getenv())
                            .putAll(overrideEnvBuilder.build())
                            .put("jmxPort", valueOf(findAvailableTcpPort()))
                            .put("symbolsCutterPath", getBuildPath("metrika/java/tools/symbols-cutter/symbols-cutter"))
                            .put("itaniumDemangler", ProgramsPaths.llvmCxxFiltPath())
                            .put("swiftDemangler", ProgramsPaths.swiftDemanglePath())
                            .put("inputQueuesRootPath", settings.getInputQueuesRoot())
                            .put("outputQueuesRootPath", settings.getOutputQueuesRoot())
                            .put("outputDataBase", settings.getOutputDataBase())
                            .build()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        System.setProperty(XmlPropertyConfigurer.RESOURCE_KEY, configFile);
        System.setProperty("jmxDefaultDomain", MobmetCrashDecoderProcessingTest.class.getName());
    }

}
