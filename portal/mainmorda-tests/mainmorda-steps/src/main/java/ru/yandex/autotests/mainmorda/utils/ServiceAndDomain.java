package ru.yandex.autotests.mainmorda.utils;

import ru.yandex.autotests.utils.morda.url.Domain;

/**
* User: ivannik
* Date: 01.07.2014
*/
public class ServiceAndDomain {
    private Domain domain;
    private String serviceId;

    public ServiceAndDomain(Domain domain, String serviceId) {
        this.domain = domain;
        this.serviceId = serviceId;
    }

    public static ServiceAndDomain snd(Domain domain, String serviceId) {
        return new ServiceAndDomain(domain, serviceId);
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof ServiceAndDomain)) {
            return false;
        }
        ServiceAndDomain sd = (ServiceAndDomain) obj;
        return domain.equals(sd.domain) && serviceId.equals(sd.serviceId);
    }

    @Override
    public int hashCode() {
        return domain.hashCode() + serviceId.hashCode() + 42;
    }
}
