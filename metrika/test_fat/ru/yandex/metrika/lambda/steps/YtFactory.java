package ru.yandex.metrika.lambda.steps;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.impl.YtUtils;
import ru.yandex.metrika.dbclients.yt.YtProperties;

@Component
public class YtFactory {
    @Autowired
    private YtProperties ytProperties;

    private Yt cachedYt;

    public Yt getYt() {
        if (cachedYt == null) {
            cachedYt = ytProperties.getProxies().stream().map(p -> YtUtils.http(p, ytProperties.getToken())).findFirst().get();
        }
        return cachedYt;
    }
}
