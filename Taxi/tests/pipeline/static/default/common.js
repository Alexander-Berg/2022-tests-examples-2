function is_present(value) {
  return value !== null && value !== undefined;
}

function is_number(value) {
  return typeof value === 'number';
}

function is_object(value) {
  return typeof value === 'object' && value !== null;
}

function is_array_like(value) {
  return (
    Array.isArray(value) ||
    (!!value &&
      typeof value === "object" &&
      "length" in value &&
      typeof (value.length) === "number" &&
      (value.length === 0 ||
        (value.length > 0 &&
          (value.length - 1) in value)
      )
    )
  );
}

function equal(x, y) {
  if (x === y) {
    return true;
  } else if (is_number(x) && is_number(y)) {
    return Math.abs(x - y) <= Number.EPSILON;
  } else if (is_object(x) && is_object(y)) {
    if (is_array_like(x) !== is_array_like(y)) {
      return false;
    }
    if (Object.keys(x).length !== Object.keys(y).length) {
      return false;
    }
    for (var prop in x) {
      if (y.hasOwnProperty(prop)) {
        if (!equal(x[prop], y[prop])) {
          return false;
        }
      } else {
        return false;
      }
    }
    return true;
  } else {
    return false;
  }
}

function assert(ok, msg, id) {
  if (!ok) {
    throw `assert failed: ${id ? `[${id}] ` : ''}${msg}`;
  }
}

function assert_eq(expected, actual, id) {
  if (!equal(expected, actual)) {
    throw `assert failed: ${id ? `[${id}] ` : ''}expected: ${JSON.stringify(expected)}; actual: ${JSON.stringify(actual)}`;
  }
}

function assert_throw_msg_contains(fn, in_msg, id) {
  const error_start = `${id ? `[${id}] ` : ''}expected to have "${in_msg}" in exception message`;

  try {
    fn();
  } catch (ex) {
    if (ex.message.indexOf(in_msg) === -1) {
      throw `${error_start}, got: "${ex.message}"`;
    }
    return;
  }

  assert(false,  `${error_start}, but it didn't throw`);
}
