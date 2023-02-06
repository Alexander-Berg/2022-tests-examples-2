package ru.yandex.metrika.cdp.api.users;

import java.util.Objects;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanDefinitionHolder;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;

public class UserCreatorBeanFactoryPostProcessor implements BeanFactoryPostProcessor {

    /**
     * Это такой сложный хак, который подменяет bean definition для бина UserCreator, чтобы заменить его на наследника,
     * а именно на TestUsersAwareUserCreator, который переопределяет метод резолва логина по uid для тесового пользователя
     */
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        ((BeanDefinitionHolder)
                Objects.requireNonNull(
                beanFactory.getBeanDefinition("metrikaRbac")
                        .getPropertyValues().get("userCreator"))
        )
                .getBeanDefinition().setBeanClassName(TestUsersAwareUserCreator.class.getName());
    }
}
