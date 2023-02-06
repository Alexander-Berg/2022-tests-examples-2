package ru.yandex.autotests.morda.rules.proxy.actions;

import net.lightbody.bmp.core.har.Har;
import org.apache.log4j.Logger;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public abstract class HarAction<T> extends Action<T> {

    protected final Logger LOG = Logger.getLogger(this.getClass());

    public HarAction(T rule) {
        super(rule);
    }

    public abstract T record();

    public abstract Har get();

    @Override
    public void perform() {
        LOG.info("Recording HAR");
    }
}
