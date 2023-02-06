
from ci_tools import report


@report('ikars', 'basic_test.py', tg_bot=True, tg_login='iiggy')
def main():
    raise AttributeError("Fuck'em all!")


if __name__ == '__main__':
    main()
