INSERT INTO login_bind_place
(
  place_id,
  login
)
VALUES
(
 123,
 'a'
),
(
 123,
 'b'
),
(
 321,
 'c'
),
(
 123,
 'd'
);

INSERT INTO line
(
  line_name
)
VALUES
(
 'a'
),
(
 'b'
),
(
 'c'
),
(
 'd'
);


INSERT INTO line_bind_place
(
  place_id,
  line_id
)
VALUES
(
 0,
 null
),
(
 123,
 1
),
(
 1234,
 1
),
(
 321,
 2
),
(
 4321,
 2
);
