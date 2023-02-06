package ru.yandex.autotests.mordabackend.actions;

import ru.yandex.autotests.mordabackend.MordaClient;

import javax.ws.rs.client.Client;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.05.14
 */
public abstract class AbstractActions {
    protected MordaClient mordaClient;
    protected Client client;

    protected AbstractActions(MordaClient mordaClient, Client client) {
        this.mordaClient = mordaClient;
        this.client = client;
    }
}
