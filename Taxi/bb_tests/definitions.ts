export type CommonError = {
    code: string;
    message: string;
    details: {
        http_code?: string;
        meta_code?: string;
        debug_message?: string;
    };
};
export type ServiceType = 'loan' | 'payment';
/**
 * Статусы заказа. Схема перемещения заказа по статусам описана здесь https://miro.com/app/board/o9J_l46a_s8=/
 * */
export type OrderStatus = 'new' | 'processing' | 'approved' | 'commited' | 'refunded' | 'partially_refunded' | 'failed';
export type RefundStatus = 'draft' | 'processing' | 'failed' | 'approved';
export type OrderRefundStatus = 'new' | 'processing' | 'approved' | 'failed';
export type PlanStatus = 'draft' | 'confirmed' | 'approved' | 'rejected' | 'completed' | 'expired' | 'canceled';
export type PlanPaymentStatus = 'paid' | 'failed' | 'coming' | 'canceled';
/**
 * стоимость товаров, на которые пользователю можно дать рассрочку, в рублях
 * */
export type Money = string;
export type User = {
    id?: string;
    yuid?: number;
    personal_data?: PersonalData;
};
export type PersonalData = {
    name?: string;
    birth_date?: string;
    phone?: string;
    email?: string;
    checks?: PersonalDataChecks;
};
/**
 * Статусы проверок заполнения персональных данных.
 * */
export type PersonalDataChecks = {
    name?: CheckStatus;
    birth_date?: CheckStatus;
    phone?: CheckStatus;
    email?: CheckStatus;
};
export type CheckStatus = 'empty' | 'draft' | 'progress' | 'error' | 'ok';
/**
 * Когда этот платёж первый в списке, считаем его первым платежом, без которого не выдаётся рассрочка.
 * */
export type RegularPayment = {
    amount?: Money;
    datetime: string;
    /**
     * Статус регулярного платежа
     * */
    payment_status?: PlanPaymentStatus;
};
export type Plan = {
    id: string;
    user_id: string;
    /**
     * тип плана
     * */
    class_name: string;
    /**
     * имя конструктора, который построил план
     * */
    constructor?: string;
    status: PlanStatus;
    /**
     * причина отказа
     * */
    rejection_reason?: 'payment_error' | 'common_error';
    details?: {
        /**
         * Сумма первоначальноого платежа
         * */
        deposit?: Money;
        /**
         * Сумма выданная в рассрочку
         * */
        loan?: Money;
        /**
         * Первый платежа включает в себя сумму депозита выше + платеж по рассрочке
         * */
        payments?: RegularPayment[];
    };
    refund?: {
        /**
         * Сколько вернули из основного платежа
         * */
        payment?: Money;
        /**
         * Сколько вренули из рассрочки
         * */
        loan?: Money;
    };
    current_payment_context?: {
        type?: 'web_form' | 'link_3ds' | 'auto';
        /**
         * Ссылка для открытия формы 3ds или формы поплаты. По умолчанию отсутствует. Появился только после /order/confirm.
         * */
        url?: string;
        payment_status?: 'wait' | 'ok' | 'failed';
        last_payment_ts?: string;
        /**
         * Карта, с которой был выполнен последний платёж.
         * */
        card?: {
            mask?: string;
            payment_system?: string;
        };
    };
};
