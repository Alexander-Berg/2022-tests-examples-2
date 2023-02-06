#include <algorithm>

#include <libproc.h>
#include <sys/proc_info.h>

#include <boost/algorithm/string/predicate.hpp>

namespace testing {

inline size_t OpenFilesCountWithPrefixOnMac(const std::string& prefix_path) {
  size_t result{0};

  const auto pid = getpid();
  // Figure out the size of the buffer needed to hold the list of open FDs
  int buffer_size = proc_pidinfo(pid, PROC_PIDLISTFDS, 0, 0, 0);
  if (buffer_size == -1) {
    return -1;
  }

  // Get the list of open FDs
  struct proc_fdinfo* proc_fd_info = (struct proc_fdinfo*)malloc(buffer_size);
  if (!proc_fd_info) {
    return -1;
  }
  buffer_size =
      proc_pidinfo(pid, PROC_PIDLISTFDS, 0, proc_fd_info, buffer_size);
  if (buffer_size < 0) {
    free(proc_fd_info);
    return -1;
  }
  int num_of_fds = buffer_size / PROC_PIDLISTFD_SIZE;

  for (int i = 0; i < num_of_fds; ++i) {
    if (proc_fd_info[i].proc_fdtype == PROX_FDTYPE_VNODE) {
      struct vnode_fdinfowithpath vnode_info;
      int bytes_used =
          proc_pidfdinfo(pid, proc_fd_info[i].proc_fd, PROC_PIDFDVNODEPATHINFO,
                         &vnode_info, PROC_PIDFDVNODEPATHINFO_SIZE);
      if (bytes_used == PROC_PIDFDVNODEPATHINFO_SIZE) {
        if (boost::algorithm::starts_with(std::string(vnode_info.pvip.vip_path),
                                          prefix_path)) {
          ++result;
        }
      } else if (bytes_used < 0) {
        free(proc_fd_info);
        return -1;
      }
    }
  }
  free(proc_fd_info);
  return result;
}

}  // namespace testing
