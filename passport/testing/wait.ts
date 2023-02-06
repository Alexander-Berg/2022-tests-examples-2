export function wait(delay = Math.random() * 1500) {
  return new Promise((resolve) => setTimeout(resolve, delay));
}
