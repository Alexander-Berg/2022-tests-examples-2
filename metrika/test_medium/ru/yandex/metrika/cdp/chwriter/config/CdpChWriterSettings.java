package ru.yandex.metrika.cdp.chwriter.config;

import org.springframework.stereotype.Component;

@Component
public class CdpChWriterSettings {
    private String ordersPoolName = "updated-orders-consumer-read";
    private String ordersConsumer = "updated-orders-consumer";
    private String ordersTopic = "updated-orders-topic";
    private String clientsPoolName = "updated-clients-consumer-read";
    private String clientsConsumer = "updated-clients-consumer";
    private String clientsTopic = "updated-clients-topic";
    private String cdpSchedulerTypeMatchingChangesSourceIdPrefix = "cdp-scheduler-type-matching-changes";
    private String cdpCryptaIdMatcherSourceIdPrefix = "cdp-cryptaid-matcher-writer-source";
    private String cdpMatcherSourceIdPrefix = "cdp-matcher-writer-source";
    private String cdpCoreSourceIdPrefix = "cdp-core-writer-source";
    private String matchingDataTablesPrefix = "matching";
    private String metaDataTablesPrefix = "ch_writer_meta";
    private String clientsDataTablePrefix = "clients_data";

    public String getOrdersPoolName() {
        return ordersPoolName;
    }

    public String getOrdersConsumer() {
        return ordersConsumer;
    }

    public String getOrdersTopic() {
        return ordersTopic;
    }

    public String getClientsPoolName() {
        return clientsPoolName;
    }

    public String getClientsConsumer() {
        return clientsConsumer;
    }

    public String getClientsTopic() {
        return clientsTopic;
    }

    public String getCdpSchedulerTypeMatchingChangesSourceIdPrefix() {
        return cdpSchedulerTypeMatchingChangesSourceIdPrefix;
    }

    public String getCdpCryptaIdMatcherSourceIdPrefix() {
        return cdpCryptaIdMatcherSourceIdPrefix;
    }

    public String getCdpMatcherSourceIdPrefix() {
        return cdpMatcherSourceIdPrefix;
    }

    public String getCdpCoreSourceIdPrefix() {
        return cdpCoreSourceIdPrefix;
    }

    public String getMatchingDataTablesPrefix() {
        return matchingDataTablesPrefix;
    }

    public String getMetaDataTablesPrefix() {
        return metaDataTablesPrefix;
    }

    public String getClientsDataTablePrefix() {
        return clientsDataTablePrefix;
    }

    public void setOrdersPoolName(String ordersPoolName) {
        this.ordersPoolName = ordersPoolName;
    }

    public void setOrdersConsumer(String ordersConsumer) {
        this.ordersConsumer = ordersConsumer;
    }

    public void setOrdersTopic(String ordersTopic) {
        this.ordersTopic = ordersTopic;
    }

    public void setClientsPoolName(String clientsPoolName) {
        this.clientsPoolName = clientsPoolName;
    }

    public void setClientsConsumer(String clientsConsumer) {
        this.clientsConsumer = clientsConsumer;
    }

    public void setClientsTopic(String clientsTopic) {
        this.clientsTopic = clientsTopic;
    }

    public void setCdpSchedulerTypeMatchingChangesSourceIdPrefix(String cdpSchedulerTypeMatchingChangesSourceIdPrefix) {
        this.cdpSchedulerTypeMatchingChangesSourceIdPrefix = cdpSchedulerTypeMatchingChangesSourceIdPrefix;
    }

    public void setCdpCryptaIdMatcherSourceIdPrefix(String cdpCryptaIdMatcherSourceIdPrefix) {
        this.cdpCryptaIdMatcherSourceIdPrefix = cdpCryptaIdMatcherSourceIdPrefix;
    }

    public void setCdpMatcherSourceIdPrefix(String cdpMatcherSourceIdPrefix) {
        this.cdpMatcherSourceIdPrefix = cdpMatcherSourceIdPrefix;
    }

    public void setCdpCoreSourceIdPrefix(String cdpCoreSourceIdPrefix) {
        this.cdpCoreSourceIdPrefix = cdpCoreSourceIdPrefix;
    }

    public void setMatchingDataTablesPrefix(String matchingDataTablesPrefix) {
        this.matchingDataTablesPrefix = matchingDataTablesPrefix;
    }

    public void setMetaDataTablesPrefix(String metaDataTablesPrefix) {
        this.metaDataTablesPrefix = metaDataTablesPrefix;
    }

    public void setClientsDataTablePrefix(String clientsDataTablePrefix) {
        this.clientsDataTablePrefix = clientsDataTablePrefix;
    }
}
