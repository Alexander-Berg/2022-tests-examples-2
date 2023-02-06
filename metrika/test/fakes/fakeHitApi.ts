const fakeHitApi = {
  success: false,

  setSuccess (success: boolean) {
    this.success = success
  },

  fakeCall (methodName: string) {
    return this.success
      ? Promise.resolve({data: methodName})
      : Promise.reject(new Error(methodName))
  },

  fetchHit () {
    return this.fakeCall('fetchHit')
  },

  getVisitInfo () {
    return this.fakeCall('getVisitInfo')
  },

  fetchHitsList () {
    return this.fakeCall('fetchHitsList')
  },

  setFavorite (isFavorite: boolean) {
    return this.fakeCall('setFavorite')
  },

  setComment (commentText: string) {
    return this.fakeCall('setComment')
  },
}

export default fakeHitApi
