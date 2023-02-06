import {ServiceType, Money, OrderStatus, Plan, RefundStatus, OrderRefundStatus} from './definitions';

export type Service = {
    type: ServiceType;
    amount: Money;
    currency: string;
    items: ServiceItem[];
};
export type ServiceItem = {
    item_code: string;
    /**
     * Число купленных товаров. Пока не делаем возможность покупки нештучных товаров.
     * */
    count: number;
    category?: string;
    shop_id?: string;
    /**
     * Название товара
     * */
    title?: string;
    price?: Money;
};
export type Order = {
    order_id: string;
    /**
     * Разная информация о продавце.
     * */
    consumer?: {
        /**
         * идентификатор продавца
         * */
        id?: string;
        /**
         * отображаемое название продавца
         * */
        title?: string;
    };
    order_meta: {
        /**
         * id заказа в системе мерчанта
         * */
        external_id?: string;
        /**
         * Выбранная для оплаты карта в трасте (выбранная еще в маркете)
         * */
        card_id?: string;
        /**
         * Урл для отправки события обновления статуса по платежу
         * */
        callback_url?: string;
        /**
         * Ранее сформированный план рассрочки (содержит в себе корзину
         * */
        plan_id?: string;
        /**
         * Дата-время создания заказа
         * */
        created_at?: string;
    };
    /**
     * Информация о том, какие товары каким образом были оплачены. При отображении списка товаров в Личном кабинете, надо слить списки для каждого типа сервисов в один.
     * */
    services: Service[];
    user_id: number;
    status: OrderStatus;
    plan?: Plan;
};
export type BillingType = 'BNPL';
export type RefundRaw = {
    id: number;
    payment_id: string;
    refund_id: string;
    internal_refund_id: string;
    session_id: string;
    order_id: number;
    sum: number;
    status: RefundStatus;
    created_at: string;
    last_update: string;
    billing_type: BillingType;
    user_id: string;
};
export type Refund = {
    refund_id: string;
    status: RefundStatus;
    plan_id: string;
    order_id: string;
    user_id: string;
    /**
     * Дата-время создания возврата
     * */
    created_at?: string;
    /**
     * Информация о том, какие услуги возвращать. Опционально может присутствовать со список товаров.
     * */
    services?: Service[];
};
export type OrderRefundReason = 'refunded' | 'canceled';
export type OrderRefund = {
    order_id: string;
    plan_id: string;
    user_id: string;
    merchant_id: string;
    sum: Money;
    /**
     * Дата-время создания возврата
     * */
    created_at: string;
    refund_id: string;
    status: OrderRefundStatus;
    callback_url: string;
    reason: OrderRefundReason;
    /**
     * Информация о том, какие услуги возвращать. Опционально может присутствовать со список товаров.
     * */
    services?: Service[];
    annotation?: {
        payment?: Money;
        loan?: Money;
    };
};
export type CourierMeta = {
    full_address?: string;
    apartment?: string;
    entrance?: string;
    floor?: string;
    intercom?: string;
    comment?: string;
};
export type PickupMeta = {
    address?: string;
    pickup_point_id?: string;
};
