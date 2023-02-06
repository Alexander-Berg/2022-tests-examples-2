package ru.yandex.autotests.metrika.appmetrica.data;

import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelismControl;

import javax.annotation.Nullable;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.LAYER;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.appById;

public class ParallellismUtils {

    public static void setCurrentLayerByApp(@Nullable Long appId) {
        if (appId != null) {
            setCurrentLayerByApp(appById.get(appId));
        }
    }

    public static void setCurrentLayerByApp(@Nullable Application application) {
        if (application != null) {
            setCurrentLayer(application.get(LAYER));
        }
    }

    public static void setCurrentLayer(int layer) {
        ParallelismControl.setParticularSemaphoreId(layer);
    }

    public static void resetCurrentLayer() {
        ParallelismControl.resetParticularSemaphoreId();
    }

}
