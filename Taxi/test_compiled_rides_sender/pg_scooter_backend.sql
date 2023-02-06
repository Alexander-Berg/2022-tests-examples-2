CREATE TABLE IF NOT EXISTS public.compiled_rides (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    session_id TEXT NOT NULL,
    object_id uuid,
    price integer NOT NULL,
    duration integer NOT NULL,
    start integer NOT NULL,
    finish integer NOT NULL,
    meta JSON,
    meta_proto TEXT,
    hard_proto TEXT
);

TRUNCATE TABLE public.compiled_rides;
INSERT INTO
  public.compiled_rides (
    history_event_id,
    history_user_id,
    history_action,
    history_timestamp,
    session_id,
    object_id,
    price,
    duration,
    start,
    finish,
    meta_proto,
    hard_proto
  ) VALUES
  (
    492297,
    'stub_history_user_id',
    'add',
    1638475550,
    'stub_session_id',
    '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid,
    777,
    111,
    1638474874, -- 2021-12-02T19:54:34+00:00
    1638475550, -- 2021-12-02T20:05:50+00:00
    'CqgBCH4QvAQaOgieJRoL0JIg0L/Rg9GC0LgiEG9sZF9zdGF0ZV9yaWRpbmcyDjkg0LzQuNC9IDMyINGBOLwERQAAAAAaRgi4Fxor0KHRgtC+0LjQvNC+0YHRgtGMINCx0YDQvtC90LjRgNC+0LLQsNC90LjRjyIPYWNjZXB0YW5jZV9jb3N0RQAAAAAaGwjWPBoK0JjRgtC+0LPQviIFdG90YWxFAAAAACAAEl8KKgkAAACgVIlGQBEAAADg63xDQB0AAAAAJc3MzD0oATCzoKaNBjjG+KWNBhIqCQAAAMDEh0ZAEQAAAKAYe0NAHQAAAAAlzczMPSgBMPunpo0GOPunpo0GHYAYDEAgASIkCM+ipo0GEhVvbGRfc3RhdGVfcmVzZXJ2YXRpb24YACCfzc4UIh8IzKOmjQYSEG9sZF9zdGF0ZV9yaWRpbmcYAyCJzs4UIiQIiKimjQYSFW9sZF9zdGF0ZV9yZXNlcnZhdGlvbhgDIMbRzhQiJAiJqKaNBhIVb2xkX3N0YXRlX3Jlc2VydmF0aW9uGAEgx9HOFCo00J/QvtC80LjQvdGD0YLQvdGL0Lkg0YLQsNGA0LjRhCBb0JrRgNCw0YHQvdC+0LTQsNGAXTAAOMyjpo0GSLwE',
    'eJztV0tsG0UY/sfrVIuDUsdQSF2hLK5XqlKttF6P91FasrZjK4oQFzjwEFrGu2tw45fsDQQJIScglLRUiCChEiQaHkVRTiFwMCh1o1YCKUrLugeEOEFRhUgvPfSAemJsE1rRqlS8cvGO9O3/nn92/sO3vncG2NMffnJsh//yxxSDe1UiE2KKWFCliCWTqCjEsqYdlW1LkKKZjKhgMxTWsClmNUsRRCxjAYu2JpAY1gRJIRkrE4vYiqUNhWNZWxLNiCVQl0qjiCIQkUSESMQysalmsmqMSNg94TbcVbfunmq+2pymeNT9gqPCcrPm1puvcU+781Rabk65p2jg5y37MwdAd19nRiGT8Ol3we9P8O4XSX48V3zOcHIFex9Ie9nvvP1/eHeV8pZRdYhjGxW7aldeIE6uVByFw33UWLRIxTFK2axdqSzdw15D/qvMQG1hBwc6jNUCPMCCzp/beOQQ/+wTl4apyrXUjYP8kacWhvmTYzjBGz/vSVBHTec9jWMP8/PvPjnM/3TyvUO8A0d16oC1/x+Av9RqbeWXdmvUFnrs7KPb1Mt/BjW9c1SA+5IUAsktdftb60IXutCFLlyHK3EKa/p2t9EBoFAb/ocF/q2GhvzFXNHOlByjQCaNcn6iOgR03RnbgjtYf4trtTKfhzJMokUEywjqCM6gcd+or4e9ygQg0EPZUgCCXhYCMCax9fupst83mCFV2yCmaZcpuzJto1zJURyvkGqxRMnWrta3ewBqD6UCgx0GN3NW798Sdm8JXO1HtI7YLYZ2AfUS0zEsO0sm8k7Ng46gv9poDvUXcsUJx65ety0hr0kq1hLqK5QyuTzNIS8V7CItD98juPhn8yYKa1pC1kZkSUjjpCJgKTkiaFJCEdJyXEpFVS0R1eQZD8x74Izn5v3Wb2G76AnsDvG9Fy6/nNQf3KfNvfX4bFrf9MCvHjTNwBwD8wwsMrDCwJeM1yGTuTUGrTOcJGqSJGexZMoyFlVVjdgZrIl2FlPaLquiy6AfGNhk4AoD1xhMymV6Dqc0bheFiISNWDqN8YgkCvFkko6SHFeEhJaOCQoeScnRaCqZ1OLHvbDkhcAiYl/xr3qDB9j3+WCvO8e5p9tDUw/5b2DSOYsSbqlP4zpjxUUlrjmlrnpTrQsMpuk4BPe7H9C0BnWvuo3mVHO6+QbnfkrnrEGnrN5+r7jLbfnN0M4bbtIsVZ1OnT3stweDPvd4u85nbiPU45Qckm87OQi+jXxh9pvWX0zg1ix/ALgT587f6xtkNz5qRd10ggGGmz1PA8LszOJtyjDcV8121OztohD3NY06vFOVJVXWxKioyDFFjf4GrP5FGg=='
  );
