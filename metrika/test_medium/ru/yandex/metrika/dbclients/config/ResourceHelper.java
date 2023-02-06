package ru.yandex.metrika.dbclients.config;

import java.util.stream.Stream;

import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

public class ResourceHelper {

    public static Resource[] mysqlResources(String... scripts) {
        return resources("../mysql/", scripts);
    }

    public static Resource[] resources(String prefix, String... scripts) {
        return Stream.of(scripts)
                .map(s -> new ClassPathResource(prefix + s, ResourceHelper.class))
                .toArray(Resource[]::new);
    }
}
