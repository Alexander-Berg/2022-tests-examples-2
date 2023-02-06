package ru.yandex.metrika.cdp.chwriter.tests.medium;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.annotation.Nonnull;

import gnu.trove.TLongCollection;
import gnu.trove.set.TLongSet;
import gnu.trove.set.hash.TLongHashSet;

import ru.yandex.metrika.cdp.chwriter.data.ClientChRow;
import ru.yandex.metrika.cdp.chwriter.data.OrderAggregates;
import ru.yandex.metrika.cdp.chwriter.data.OrderChRow;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.processing.dto.export.ClientVersion;
import ru.yandex.metrika.cdp.processing.dto.export.OrderVersion;


// объединяет в себе все необходимые для тестов данные,
// так как для работы демона необходимы связанные между собой данные в табличках
// принимает в себя все входные данные и умеет посчитать ожидаемые значения
public class CdpChWriterTestStateHolder {
    private List<Order> orders = List.of();
    private Map<OrderKey, OrderVersion> orderVersions = Map.of();

    private Map<ClientKey, List<OrderJoinedWithOrderStatus>> joinedRows = Map.of();

    private List<Client> clients = List.of();
    private Map<ClientKey, ClientVersion> clientVersions = Map.of();

    private Map<ClientKey, TLongSet> userIds = Map.of();
    private Map<ClientKey, TLongSet> cryptaIds = Map.of();
    private Map<ClientKey, TLongSet> gluedIds = Map.of();

    private Map<Integer, List<OrderStatus>> orderStatuses = Map.of();

    public CdpChWriterTestStateHolder() {
    }

    @Nonnull
    private Map<ClientKey, List<OrderJoinedWithOrderStatus>> joinOrderWithOrderStatuses(List<Order> orders, Map<Integer, List<OrderStatus>> orderStatuses) {
        return getClientKeys().stream()
                .collect(Collectors.toMap(Function.identity(),
                                clientKey -> orders.stream()
                                        .filter(order -> clientKey.getCdpUid() == order.getCdpUid() && clientKey.getCounterId() == order.getCounterId())
                                        .map(order -> orderStatuses.get(clientKey.getCounterId()).stream()
                                                .filter(os -> order.getOrderStatus().equals(os.getId()))
                                                .map(os -> new OrderJoinedWithOrderStatus(order, os))
                                                .filter(row -> !row.isSpam())
                                                .collect(Collectors.toList()))
                                        .flatMap(Collection::stream)
                                        .collect(Collectors.toList())
                        )
                );
    }

    public OrderAggregates getOrderAggregates(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        long sumRevenue = getSumRevenue(clientKey);
        long ltv = getLtv(clientKey);
        Instant firstOrderCreate = getFirstOrderCreate(clientKey);
        Instant lastOrderCreate = getLastOrderCreate(clientKey);
        Instant firstOrderFinish = getFirstOrderFinish(clientKey);
        Instant lastOrderFinish = getLastOrderFinish(clientKey);
        int completedOrders = getCompletedOrdersCount(clientKey);
        int createdOrders = getCreatedOrdersCount(clientKey);
        int paidOrders = getPaidOrdersCount(clientKey);
        return new OrderAggregates(clientKey, sumRevenue, ltv, firstOrderCreate, lastOrderCreate, firstOrderFinish, lastOrderFinish, completedOrders, createdOrders, paidOrders);
    }

    public int getPaidOrdersCount(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return (int) joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isPaid).count();
    }

    public int getCreatedOrdersCount(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).size();
    }

    public int getCompletedOrdersCount(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return (int) joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isCompleted).count();
    }

    public Instant getLastOrderFinish(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isPaidAndHasNonNullTime).map(OrderJoinedWithOrderStatus::getFinishTimeIfPaid).max(Comparator.naturalOrder()).orElse(Instant.ofEpochSecond(0));
    }

    public Instant getFirstOrderFinish(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isPaidAndHasNonNullTime).map(OrderJoinedWithOrderStatus::getFinishTimeIfPaid).min(Comparator.naturalOrder()).orElse(Instant.ofEpochSecond(0));
    }

    public Instant getLastOrderCreate(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().map(OrderJoinedWithOrderStatus::getCreateDateTime).max(Comparator.naturalOrder()).orElse(null);
    }

    public Instant getFirstOrderCreate(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().map(OrderJoinedWithOrderStatus::getCreateDateTime).min(Comparator.naturalOrder()).orElse(null);
    }

    public long getLtv(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isPaid).mapToLong(OrderJoinedWithOrderStatus::getLtv).sum();
    }

    public long getSumRevenue(ClientKey clientKey) {
        if (joinedRows.isEmpty()) {
            joinedRows = joinOrderWithOrderStatuses(orders, orderStatuses);
        }
        return joinedRows.get(clientKey).stream().filter(OrderJoinedWithOrderStatus::isPaid).mapToLong(OrderJoinedWithOrderStatus::getRevenue).sum();
    }

    public Map<ClientKey, List<OrderJoinedWithOrderStatus>> getJoinedRows() {
        return joinedRows;
    }

    private long[] getLongArray(TLongCollection primitiveCollection) {
        return primitiveCollection.toArray();
    }

    public List<OrderKey> getOrderKeys() {
        return orders.stream().map(Order::getKey).collect(Collectors.toList());
    }

    public List<ClientKey> getClientKeys() {
        return clients.stream().map(Client::getKey).collect(Collectors.toList());
    }

    public List<Client> getClients() {
        return clients;
    }

    public List<Order> getOrders() {
        return orders;
    }

    public Map<ClientKey, ClientVersion> getClientVersions() {
        return clientVersions;
    }

    public Map<OrderKey, OrderVersion> getOrderVersions() {
        return orderVersions;
    }

    public Map<ClientKey, TLongSet> getUserIds() {
        return userIds;
    }

    public Map<ClientKey, TLongSet> getCryptaIds() {
        return cryptaIds;
    }

    public Map<ClientKey, TLongSet> getGluedIds() {
        return gluedIds;
    }

    public Map<ClientKey, ClientChRow> getClientChRows() {
        return clients.stream().collect(Collectors.toMap(
                Client::getKey,
                client -> new ClientChRow(client,
                        clientVersions.get(client.getKey()),
                        getOrderAggregates(client.getKey()),
                        userIds.get(client.getKey()),
                        cryptaIds.get(client.getKey()),
                        gluedIds.get(client.getKey()))));
    }

    public Map<OrderKey, OrderChRow> getOrderChRows() {
        return orders.stream().collect(Collectors.toMap(
                Order::getKey,
                order -> new OrderChRow(order, orderVersions.get(order.getKey()))));
    }

    public void incrementAllOrderVersions() {
        orderVersions.forEach((k, v) ->
                orderVersions.put(k, new OrderVersion(v.getKey(), v.getVersion() + 1, v.getChPartitionId())));
    }

    public void incrementAllClientVersions() {
        clientVersions.forEach((k, v) ->
                clientVersions.put(k, new ClientVersion(v.getKey(), v.getVersion() + 1, v.getChPartitionId())));
    }

    public Map<Integer, List<OrderStatus>> getOrderStatuses() {
        return orderStatuses;
    }

    public void setOrders(List<Order> orders) {
        this.orders = new ArrayList<>(orders);
    }

    public void setOrderVersions(Map<OrderKey, OrderVersion> orderVersions) {
        this.orderVersions = new HashMap<>(orderVersions);
    }

    public void setClients(List<Client> clients) {
        this.clients = new ArrayList<>(clients);
    }

    public void setClientVersions(Map<ClientKey, ClientVersion> clientVersions) {
        this.clientVersions = new HashMap<>(clientVersions);
    }

    public void setUserIds(Map<ClientKey, TLongSet> userIds) {
        this.userIds = new HashMap<>();
        userIds.forEach((k, v) -> {
            if (!this.userIds.containsKey(k)) {
                this.userIds.put(k, new TLongHashSet());
            }
            this.userIds.get(k).addAll(v);
        });
    }

    public void setCryptaIds(Map<ClientKey, TLongSet> cryptaIds) {
        this.cryptaIds = new HashMap<>();
        cryptaIds.forEach((k, v) -> {
            if (!this.cryptaIds.containsKey(k)) {
                this.cryptaIds.put(k, new TLongHashSet());
            }
            this.cryptaIds.get(k).addAll(v);
        });
    }

    public void setGluedIds(Map<ClientKey, TLongSet> gluedIds) {
        this.gluedIds = new HashMap<>();
        gluedIds.forEach((k, v) -> {
            if (!this.gluedIds.containsKey(k)) {
                this.gluedIds.put(k, new TLongHashSet());
            }
            this.gluedIds.get(k).addAll(v);
        });
    }

    public void setOrderStatuses(Map<Integer, List<OrderStatus>> orderStatuses) {
        this.orderStatuses = new HashMap<>();
        orderStatuses.forEach((k, v) -> {
            if (!this.orderStatuses.containsKey(k)) {
                this.orderStatuses.put(k, new ArrayList<>());
            }
            this.orderStatuses.get(k).addAll(v);
        });
    }

    public void updateOrders(List<Order> update) {
        orders.addAll(update);
        joinedRows = Map.of();
    }

    public void updateOrderStatuses(Map<Integer, List<OrderStatus>> update) {
        update.forEach((k, v) -> {
            if (!orderStatuses.containsKey(k)) {
                orderStatuses.put(k, new ArrayList<>());
            }
            orderStatuses.get(k).addAll(v);
        });
        joinedRows = Map.of();
    }

    public void updateClients(List<Client> update) {
        clients.addAll(update);
    }

    public void updateUserIds(Map<ClientKey, TLongSet> update) {
        updateMapToTLongSet(userIds, update);
    }

    public void updateCryptaIds(Map<ClientKey, TLongSet> update) {
        updateMapToTLongSet(cryptaIds, update);
    }

    public void updateGluedIds(Map<ClientKey, TLongSet> update) {
        updateMapToTLongSet(gluedIds, update);
    }

    private <K> void updateMapToTLongSet(Map<K, TLongSet> map, Map<K, TLongSet> update) {
        update.forEach((k, v) -> {
            if (!map.containsKey(k)) {
                map.put(k, new TLongHashSet());
            }
            map.get(k).addAll(v);
        });
    }
}
