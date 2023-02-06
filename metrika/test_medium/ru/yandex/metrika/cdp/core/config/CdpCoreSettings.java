package ru.yandex.metrika.cdp.core.config;

import org.springframework.stereotype.Component;

@Component
public class CdpCoreSettings {
    private String clientsDataTablePrefix = "clients_data";
    private String schemaDataTablePrefix = "schema";
    private String cdpClientsTopic = "cdp-clients-topic";
    private String cdpClientsConsumer = "cdp-clients-consumer";
    private String cdpClientsPoolName = "cdp-clients-pool-name";
    private String updateClientsTopic = "updated-clients-topic";
    private String sourceIdPrefix = "source-id-prefix";
    private String cdpClientIdChangeTopic = "cdp-client-id-change-topic";
    private String changedEmailsAndPhonesTopic = "changed-emails-and-phones-topic";
    private String cdpOrdersTopic = "cdp-orders-topic";
    private String cdpOrdersConsumer = "cdp-orders-consumer";
    private String cdpOrdersPoolName = "cdp-orders-pool-name";
    private String updatedOrdersTopic = "updated-orders-topic";
    private String cdpEventsTopic = "cdp-events-topic";
    private String cdpEventsConsumer = "cdp-events-consumer";
    private String cdpEventsPoolName = "cdp-events-pool-name";
    private String newEventsTopic = "new-events-topic";
    private String clientKeysConsumerPath = "client-keys-consumer";
    private String orderKeysConsumerPath = "order-keys-consumer";
    private String changedEmailsAndPhonesConsumerPath = "changed-emails-and-phones-consumer";
    private String cdpClientIdChangesConsumerPath = "cdp-client-id-change-consumer";

    public String getClientsDataTablePrefix() {
        return clientsDataTablePrefix;
    }

    public String getSchemaDataTablePrefix() {
        return schemaDataTablePrefix;
    }

    public String getCdpClientsTopic() {
        return cdpClientsTopic;
    }

    public String getCdpClientsConsumer() {
        return cdpClientsConsumer;
    }

    public String getCdpClientsPoolName() {
        return cdpClientsPoolName;
    }

    public String getUpdateClientsTopic() {
        return updateClientsTopic;
    }

    public String getSourceIdPrefix() {
        return sourceIdPrefix;
    }

    public String getCdpClientIdChangeTopic() {
        return cdpClientIdChangeTopic;
    }

    public String getChangedEmailsAndPhonesTopic() {
        return changedEmailsAndPhonesTopic;
    }

    public String getCdpOrdersTopic() {
        return cdpOrdersTopic;
    }

    public String getCdpOrdersConsumer() {
        return cdpOrdersConsumer;
    }

    public String getCdpOrdersPoolName() {
        return cdpOrdersPoolName;
    }

    public String getUpdatedOrdersTopic() {
        return updatedOrdersTopic;
    }

    public String getCdpEventsTopic() {
        return cdpEventsTopic;
    }

    public String getCdpEventsConsumer() {
        return cdpEventsConsumer;
    }

    public String getCdpEventsPoolName() {
        return cdpEventsPoolName;
    }

    public String getNewEventsTopic() {
        return newEventsTopic;
    }

    public String getClientKeysConsumerPath() {
        return clientKeysConsumerPath;
    }

    public String getOrderKeysConsumerPath() {
        return orderKeysConsumerPath;
    }

    public String getChangedEmailsAndPhonesConsumerPath() {
        return changedEmailsAndPhonesConsumerPath;
    }

    public String getCdpClientIdChangesConsumerPath() {
        return cdpClientIdChangesConsumerPath;
    }

    public void setClientsDataTablePrefix(String clientsDataTablePrefix) {
        this.clientsDataTablePrefix = clientsDataTablePrefix;
    }

    public void setSchemaDataTablePrefix(String schemaDataTablePrefix) {
        this.schemaDataTablePrefix = schemaDataTablePrefix;
    }

    public void setCdpClientsTopic(String cdpClientsTopic) {
        this.cdpClientsTopic = cdpClientsTopic;
    }

    public void setCdpClientsConsumer(String cdpClientsConsumer) {
        this.cdpClientsConsumer = cdpClientsConsumer;
    }

    public void setCdpClientsPoolName(String cdpClientsPoolName) {
        this.cdpClientsPoolName = cdpClientsPoolName;
    }

    public void setUpdateClientsTopic(String updateClientsTopic) {
        this.updateClientsTopic = updateClientsTopic;
    }

    public void setSourceIdPrefix(String sourceIdPrefix) {
        this.sourceIdPrefix = sourceIdPrefix;
    }

    public void setCdpClientIdChangeTopic(String cdpClientIdChangeTopic) {
        this.cdpClientIdChangeTopic = cdpClientIdChangeTopic;
    }

    public void setChangedEmailsAndPhonesTopic(String changedEmailsAndPhonesTopic) {
        this.changedEmailsAndPhonesTopic = changedEmailsAndPhonesTopic;
    }

    public void setCdpOrdersTopic(String cdpOrdersTopic) {
        this.cdpOrdersTopic = cdpOrdersTopic;
    }

    public void setCdpOrdersConsumer(String cdpOrdersConsumer) {
        this.cdpOrdersConsumer = cdpOrdersConsumer;
    }

    public void setCdpOrdersPoolName(String cdpOrdersPoolName) {
        this.cdpOrdersPoolName = cdpOrdersPoolName;
    }

    public void setUpdatedOrdersTopic(String updatedOrdersTopic) {
        this.updatedOrdersTopic = updatedOrdersTopic;
    }

    public void setCdpEventsTopic(String cdpEventsTopic) {
        this.cdpEventsTopic = cdpEventsTopic;
    }

    public void setCdpEventsConsumer(String cdpEventsConsumer) {
        this.cdpEventsConsumer = cdpEventsConsumer;
    }

    public void setCdpEventsPoolName(String cdpEventsPoolName) {
        this.cdpEventsPoolName = cdpEventsPoolName;
    }

    public void setNewEventsTopic(String newEventsTopic) {
        this.newEventsTopic = newEventsTopic;
    }

    public void setClientKeysConsumerPath(String clientKeysConsumerPath) {
        this.clientKeysConsumerPath = clientKeysConsumerPath;
    }

    public void setOrderKeysConsumerPath(String orderKeysConsumerPath) {
        this.orderKeysConsumerPath = orderKeysConsumerPath;
    }

    public void setChangedEmailsAndPhonesConsumerPath(String changedEmailsAndPhonesConsumerPath) {
        this.changedEmailsAndPhonesConsumerPath = changedEmailsAndPhonesConsumerPath;
    }

    public void setCdpClientIdChangesConsumerPath(String cdpClientIdChangesConsumerPath) {
        this.cdpClientIdChangesConsumerPath = cdpClientIdChangesConsumerPath;
    }
}
