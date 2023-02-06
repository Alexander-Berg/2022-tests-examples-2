let price = -1;
let choosen_category = '';
for (let i in taxi_pricing.prices) {
    let price_data = taxi_pricing.prices[i];
    if (price < 0 || price > price_data.price) {
        price = price_data.price;
        choosen_category = price_data.category;
    }
}
if (price < 0) {
    throw 'Cannot choose taxi price: ' + JSON.stringify(taxi_pricing);
}
let surge_val = 0;
if (add_surge){
    surge_val = surge['deliveryFee'];
}
let fees = [];
for (let i in thresholds) {

    fees.push({
        delivery_cost: price + threshowlds[i].addition - commission_data.rpo_commission + surge_val,
        order_price: thresholds[i].value
    });
}
return {
    fees: fees,
    is_fallback: false,
    extra: {
        choosen_category: choosen_category,
        is_free_delivery_fee: is_free_delivery_fee,
        thresholds_free_delivery: thresholds_free_delivery,
        number_of_orders_to_set_free_delivery_fee: number_of_orders_to_set_free_delivery_fee,
        eater_orders_stats: eater_orders_stats,
        surge: surge
    }
}
