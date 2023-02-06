#include <taxi/tools/dorblu/lib/include/tokenizer.h>
#include <taxi/tools/dorblu/lib/include/error.h>

#include <iostream>

void usage(const char* prog)
{
    std::cerr << "Usage: " << prog << " [--tskv] format.conf <access.log" << std::endl;
    exit(1);
}

int main(int argc, char* argv[])
{
    const char* fname = "/var/log/nginx/access.log";
    bool is_tskv = false;
    if (argc == 2) {
        fname = argv[1];
    } else if (argc == 3) {
        if (argv[1] == std::string("--tskv")) {
        is_tskv = true;
    } else {
        usage(argv[0]);
    }
        fname = argv[2];
    } else {
        usage(argv[0]);
    }

    Tokenizer t(fname, is_tskv);

    std::cout << (std::string)(t.format()) << std::endl;

    std::string lineBuf;
    while (!std::cin.eof()) {
        std::getline(std::cin, lineBuf);

        auto result = t.tokenize(lineBuf);
        if (result) {
            std::cout << "input: " << lineBuf << std::endl;
            const auto& line = *result;
        
            std::cout << "Line:\n" << t.format().describeLine(line) << std::endl;
        }
    }

    return 0;
}
