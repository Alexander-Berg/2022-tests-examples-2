import { parse } from "@formatjs/icu-messageformat-parser";
import { expect, test } from "@jest/globals";
import { print } from "./print";

test("condenced", () => {
  expect(
    print(
      parse(`\
{gender, select,
  female {She has}
  male {He has}
  other {They have}
} {cats, plural,
  one {# cat}
  other {# cats}
} and {dogs, plural,
  one {# dog}
  other {# dogs}
}`)
    )
  ).toEqual(
    "{gender, select, female {She has} male {He has} other {They have}} {cats, plural, one {# cat} other {# cats}} and {dogs, plural, one {# dog} other {# dogs}}"
  );
});

test("exploded", () => {
  expect(
    print(
      parse(`\
{gender, select,
  female {{cats, plural,
    one {{dogs, plural,
      one {She has {cats} cat and {dogs} dog}
      other {She has {cats} cat and {dogs} dogs}
    }}
    other {{dogs, plural,
      one {She has {cats} cats and {dogs} dog}
      other {She has {cats} cats and {dogs} dogs}
    }}
  }}
  male {{cats, plural,
    one {{dogs, plural,
      one {He has {cats} cat and {dogs} dog}
      other {He has {cats} cat and {dogs} dogs}
    }}
    other {{dogs, plural,
      one {He has {cats} cats and {dogs} dog}
      other {He has {cats} cats and {dogs} dogs}
    }}
  }}
  other {{cats, plural,
    one {{dogs, plural,
      one {They have {cats} cat and {dogs} dog}
      other {They have {cats} cat and {dogs} dogs}
    }}
    other {{dogs, plural,
      one {They have {cats} cats and {dogs} dog}
      other {They have {cats} cats and {dogs} dogs}
    }}
  }}
}`)
    )
  ).toEqual(
    "{gender, select, female {{cats, plural, one {{dogs, plural, one {She has {cats} cat and {dogs} dog} other {She has {cats} cat and {dogs} dogs}}} other {{dogs, plural, one {She has {cats} cats and {dogs} dog} other {She has {cats} cats and {dogs} dogs}}}}} male {{cats, plural, one {{dogs, plural, one {He has {cats} cat and {dogs} dog} other {He has {cats} cat and {dogs} dogs}}} other {{dogs, plural, one {He has {cats} cats and {dogs} dog} other {He has {cats} cats and {dogs} dogs}}}}} other {{cats, plural, one {{dogs, plural, one {They have {cats} cat and {dogs} dog} other {They have {cats} cat and {dogs} dogs}}} other {{dogs, plural, one {They have {cats} cats and {dogs} dog} other {They have {cats} cats and {dogs} dogs}}}}}}"
  );
});

test("tags", () => {
  expect(
    print(
      parse(`\
You have <cats>{cats, plural,
  one {# cat}
  other {# cats}
}</cats> and <dogs>{dogs, plural,
  one {# dog}
  other {# dogs}
}</dogs>`)
    )
  ).toEqual(
    "You have <cats>{cats, plural, one {# cat} other {# cats}}</cats> and <dogs>{dogs, plural, one {# dog} other {# dogs}}</dogs>"
  );
});
