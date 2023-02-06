package ru.yandex.metrika.common.test.medium;

import java.io.IOException;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;

import freemarker.cache.ClassTemplateLoader;
import freemarker.core.TemplateClassResolver;
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;

public class FreemarkerUtils {

    public static String renderTemplate(String className, String templateName, Object dataModel) {
        StringWriter writer = new StringWriter();

        try {
            Configuration configuration = new Configuration(Configuration.VERSION_2_3_20);
            configuration.setTemplateLoader(new ClassTemplateLoader(FreemarkerUtils.class, className));
            configuration.setDefaultEncoding(StandardCharsets.UTF_8.displayName());
            configuration.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
            configuration.setOutputEncoding(StandardCharsets.UTF_8.name());
            configuration.setNewBuiltinClassResolver(TemplateClassResolver.ALLOWS_NOTHING_RESOLVER);

            Template template = configuration.getTemplate(templateName);
            template.process(dataModel, writer);
        } catch (IOException | TemplateException e) {
            throw new RuntimeException("Error while processing template.", e);
        }

        return writer.toString();
    }

}
