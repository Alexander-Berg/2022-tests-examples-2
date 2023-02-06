SELECT
  PushTokenType,
  argMax(DeviceIDHash, Version) as Device,
  argMax(EventValue, Version) as PushToken,
  argMax(TokenEnvironment='production', Version) AS IsProductionToken,
  argMax(AppID, Version) as AppID,
  max(Version) as PushTokenVersion
FROM mobile.total_push_token_events_layer
WHERE APIKey = %{apiKey} AND %{idCondition} AND PushTokenType IN (1, 2, 3, 4)
GROUP BY PushTokenType
HAVING notEmpty(PushToken) AND argMax(EventType, (Version, EventType = 0)) != 0
