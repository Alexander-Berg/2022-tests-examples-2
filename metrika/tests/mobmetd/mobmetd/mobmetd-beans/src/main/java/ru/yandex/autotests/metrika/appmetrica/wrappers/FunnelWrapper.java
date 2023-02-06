package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.Funnel;

public class FunnelWrapper {

    private Funnel funnel;

    public static FunnelWrapper wrap(Funnel funnel) {
        return new FunnelWrapper(funnel);
    }

    public FunnelWrapper(Funnel funnel) {
        this.funnel = funnel;
    }

    public Funnel getFunnel() {
        return funnel;
    }

    @Override
    public String toString() {
        return funnel.getName();
    }
}
