package ru.yandex.metrika.config;

import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.xml.XmlBeanDefinitionReader;
import org.springframework.core.io.ResourceLoader;

/**
 * Хаки загрузки ресурсов по разным путям на любой вкус
 * Подробнее смотри в {@link ArcadiaSourceAwareResourcePatternResolver}
 */
public class ArcadiaSourceAwareBeanDefinitionReader extends XmlBeanDefinitionReader {

    private final ArcadiaSourceAwareResourcePatternResolver resolver = new ArcadiaSourceAwareResourcePatternResolver();

    /**
     * Create new XmlBeanDefinitionReader for the given bean factory.
     *
     * @param registry the BeanFactory to load bean definitions into,
     *                 in the form of a BeanDefinitionRegistry
     */
    public ArcadiaSourceAwareBeanDefinitionReader(BeanDefinitionRegistry registry) {
        super(registry);

        setResourceLoader(resolver);
    }

    @Override
    public ResourceLoader getResourceLoader() {
        return resolver;
    }


}
