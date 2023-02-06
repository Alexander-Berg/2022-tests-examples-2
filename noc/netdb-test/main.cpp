#include <noc/matilda/common/netdb.h>

#include <contrib/phantom/pd/base/uint128.H>
#include <contrib/phantom/pd/base/in.H>
#include <contrib/phantom/pd/base/exception.H>
#include <contrib/phantom/pd/base/str.H>
#include <contrib/phantom/pd/base/in_fd.H>
#include <contrib/phantom/pd/base/fd_guard.H>

#include <contrib/phantom/pd/base/out_fd.H>

#include <fcntl.h>

namespace ct {

extern "C" int main(int argc, char *argv[]) {
    if(argc != 2)
        return 1;

    try {
        int fd = ::open(argv[1], O_RDONLY, 0);

        if(fd < 0)
            throw pd::exception_sys_t(pd::log::error, errno, "open: %m");

        pd::fd_guard_t fd_guard(fd);
        pd::in_fd_t in(16 * 1024, fd);
        pd::in_t::ptr_t ptr(in);

        netdb_t netdb(ptr);

        return 0;
    }
    catch(pd::exception_t const &ex) {
    }
    catch(...) {
        log_error("unknown exception");
    }

    return 1;
}

} // namespace ct
