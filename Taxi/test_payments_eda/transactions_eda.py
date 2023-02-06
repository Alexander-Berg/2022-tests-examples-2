def get_payment(
        mock_blackbox, wallet_account, payment_method, payment_method_id,
):
    payment = {'method': payment_method_id, 'type': payment_method}

    if payment_method == 'badge':
        payment['payer_login'] = mock_blackbox()
    elif payment_method == 'personal_wallet':
        payment['account'] = wallet_account
        payment['service'] = '32'
    else:
        payment['billing_id'] = ''
    return payment
