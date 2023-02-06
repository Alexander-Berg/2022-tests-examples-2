package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;

public class ProfileCustomAttributeWrapper {

    private final ProfileCustomAttribute attribute;

    public static ProfileCustomAttributeWrapper wrap(ProfileCustomAttribute attribute) {
        return new ProfileCustomAttributeWrapper(attribute);
    }

    private ProfileCustomAttributeWrapper(ProfileCustomAttribute attribute) {
        this.attribute = attribute;
    }

    public ProfileCustomAttribute getAttribute() {
        return attribute;
    }

    @Override
    public String toString() {
        return attribute.getName();
    }
}
