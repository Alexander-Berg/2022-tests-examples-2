package ru.yandex.metrika.schedulerd.helpers;

import com.google.common.collect.ImmutableMap;

import static java.lang.String.valueOf;
import static org.springframework.util.SocketUtils.findAvailableTcpPort;

public class JmxConfigHelper implements ConfigHelper {
    private final String testClassName; //= SchedulerdBaseTest.class.getName()

    public JmxConfigHelper(String testClassName) {
        this.testClassName = testClassName;
    }

    @Override
    public void addConfigArgs(ImmutableMap.Builder<String, String> configBuilder) {
        configBuilder.put("jmxPort", valueOf(findAvailableTcpPort()));
    }

    @Override
    public void apply() {
        System.setProperty("jmxDefaultDomain", testClassName);
    }
}
