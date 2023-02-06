#include <trackstory-shorttracks/shorttracks.hpp>

namespace trackstory::shorttracks {

class ShortTracksCacheTester {
 public:
  ShortTracksCacheTester(ShortTracksCache& cache) : cache_(cache) {}

  void CleanOldTracks() { cache_.CleanOldTracks(); }

 private:
  ShortTracksCache& cache_;
};

}  //  namespace trackstory::shorttracks
