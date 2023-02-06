package ru.yandex.autotests.mainmorda.utils;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class ServiceWithComment {
    public LinkHrefInfo serviceLink;
    public LinkHrefInfo serviceComment;

    public ServiceWithComment(LinkHrefInfo serviceLink, LinkHrefInfo serviceComment) {
        this.serviceLink = serviceLink;
        this.serviceComment = serviceComment;
    }

    @Override
    public String toString() {
        return serviceLink.toString();
    }
}
