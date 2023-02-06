export default (timeout: number = 100) => {
  return new Promise((resolve) => {
    setTimeout(resolve, timeout)
  })
}