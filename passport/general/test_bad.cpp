enum class EFoo {
    First,
    Second,
};

void bar(EFoo e) {
    switch (e) {
        case EFoo::First:
            break;
    }
}

int main() {
    bar(EFoo::First);
    return 0;
}
