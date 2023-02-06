PROGRAM()

OWNER(
  g:security
)

CFLAGS(
    -DSOME_BULLSHIT='2.8.5 \(dt dec pq3 ext lo64\)'
    -DPG_VERSION_NUM=120001
    -DHAVE_LO64=1
)

SRCS(
  fake.cpp
)

END()
