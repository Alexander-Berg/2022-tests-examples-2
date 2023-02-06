async def get_user(postgres, pd_id_user_id):
    query = f"""
    SELECT *
    FROM scooter_accumulator_bot.users
    WHERE pd_id_user_id = $1
    ORDER BY pd_id_user_id
    """
    async with postgres.master_pool.acquire() as conn:
        return await conn.fetchrow(query, pd_id_user_id)
