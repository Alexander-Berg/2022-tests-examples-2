OFFER_FETCH_SQL = 'SELECT * FROM toll_roads.offers where offer_id=$1'
OFFER_SAVE_SQL = 'INSERT INTO toll_roads.offers (offer_id) VALUES ($1)'

ORDER_FETCH_SQL = 'SELECT * FROM toll_roads.orders where order_id=$1'
ORDER_SAVE_SQL = (
    'INSERT INTO toll_roads.orders '
    '(order_id, created_at, can_switch_road, offer_id, '
    'auto_payment, point_a, point_b) '
    'VALUES ($1, $2, $3, $4, $5, $6, $7)'
)

LOG_FETCH_LAST_SQL = (
    'SELECT * FROM toll_roads.log_has_toll_road '
    'WHERE order_id=$1 ORDER BY created_at DESC LIMIT 1'
)
LOG_SAVE_SQL = (
    'INSERT INTO toll_roads.log_has_toll_road '
    '(order_id, created_at, has_toll_road) VALUES ($1, $2, $3)'
)
