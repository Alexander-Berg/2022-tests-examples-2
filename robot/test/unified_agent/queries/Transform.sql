SELECT Text, Data, Value <> "value2" as Mark, Key, Value FROM (
  SELECT Text, Data, Mark, Keys FROM (
    SELECT Text, Data, Mark, Keys FROM Input
  ) FLATTEN LIST BY Keys
) FLATTEN COLUMNS;
