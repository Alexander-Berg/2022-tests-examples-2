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
let fees = [];
for (let i in thresholds) {
  fees.push({
    delivery_cost:
        price + thresholds[i].addition - commission_data.rpo_commission,
    order_price: thresholds[i].value
  });
}
return {
  fees: fees, is_fallback: false, extra: {choosen_category: choosen_category}
}
