package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;

/**
 * Created by graev on 23/12/2016.
 */
public final class PostbackTemplateWrapper {
    private PostbackTemplate template;

    public PostbackTemplateWrapper(PostbackTemplate template) {
        this.template = template;
    }

    public PostbackTemplate getTemplate() {
        return template;
    }

    @Override
    public String toString() {
        return template.getTitle();
    }
}
