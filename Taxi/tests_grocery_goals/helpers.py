def configure_goal_reward_promocode(coupons, goal_reward_promocode):
    coupons.check_series_info_request(
        series_id=goal_reward_promocode.promocode_series,
    )
    coupons.set_series_info_response(
        body={'value': goal_reward_promocode.promocode_value},
    )


def configure_goal_reward_sku(overlord_catalog, goal_reward_sku):
    for sku in goal_reward_sku.skus:
        overlord_catalog.add_product_data(
            product_id=sku,
            title='some product name',
            image_url_template=goal_reward_sku.sku_image_url_template,
        )
