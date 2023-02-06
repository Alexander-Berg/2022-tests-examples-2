from transactions.internal import basket


def first_basket(composite_basket: basket.CompositeBasket) -> basket.Basket:
    return next(iter(composite_basket.values()), basket.Basket({}))
