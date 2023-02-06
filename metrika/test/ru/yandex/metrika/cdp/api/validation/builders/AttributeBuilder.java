package ru.yandex.metrika.cdp.api.validation.builders;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;

public final class AttributeBuilder implements NameAwareBuilder<Attribute, AttributeBuilder> {
    AttributeType type;
    private String name;
    private Boolean multivalued;
    private String humanized;
    private int counterId;

    private AttributeBuilder() {
    }

    public static AttributeBuilder anAttribute() {
        return new AttributeBuilder();
    }

    public AttributeBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public AttributeBuilder withType(AttributeType type) {
        this.type = type;
        return this;
    }

    public AttributeBuilder withMultivalued(Boolean multivalued) {
        this.multivalued = multivalued;
        return this;
    }

    public AttributeBuilder withHumanized(String humanized) {
        this.humanized = humanized;
        return this;
    }

    public AttributeBuilder withCounterId(int counterId) {
        this.counterId = counterId;
        return this;
    }

    @Override
    public Attribute build() {
        Attribute attribute = new Attribute();
        attribute.setName(name);
        attribute.setType(type);
        attribute.setMultivalued(multivalued);
        attribute.setHumanized(humanized);
        attribute.setCounterId(counterId);
        return attribute;
    }
}
