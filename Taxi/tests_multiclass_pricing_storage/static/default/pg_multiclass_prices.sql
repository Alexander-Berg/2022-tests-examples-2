INSERT INTO info VALUES ('1',
    to_jsonb('{' ||
                 '"id": "1",' ||
                 '"common":' ||
                 '{' ||
                     '"show_price_in_taximeter": true,' ||
                     '"max_distance_from_b": 500.0,' ||
                     '"destination": [35.100, 55.500]' ||
                 '},' ||
                 '"prices_info":' ||
                     '[' ||
                         '{' ||
                             '"class": "econom",' ||
                             '"prices": {' ||
                                 '"price": 350, ' ||
                                 '"price_original": 350,' ||
                                 '"driver_price": 400,' ||
                                 '"paid_supply_price": 50' ||
                             '},' ||
                             '"surge": {' ||
                                 '"value": 1.2,' ||
                                 '"surcharge": 60,' ||
                                 '"alpha": 0.8,' ||
                                 '"beta": 0.2' ||
                             '}' ||
                         '}, ' ||
                         '{' ||
                             '"class": "business",' ||
                             '"prices": {' ||
                                 '"price": 700, ' ||
                                 '"price_original": 700' ||
                             '},' ||
                             '"surge": {' ||
                                 '"value": 1.2' ||
                             '}' ||
                         '}' ||
                     ']' ||
             '}'),
    current_timestamp)
