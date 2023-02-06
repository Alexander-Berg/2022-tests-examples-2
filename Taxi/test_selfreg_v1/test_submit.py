async def test_referral_post(taxi_selfreg, mongo):
    token = 'token'

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert 'is_submitted' not in profile

    ##
    # First request
    ##
    response = await taxi_selfreg.post(
        '/selfreg/v1/submit/', params={'token': token},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['is_submitted']

    ##
    # Second request
    ##
    response = await taxi_selfreg.post(
        '/selfreg/v1/submit/', params={'token': token},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}
