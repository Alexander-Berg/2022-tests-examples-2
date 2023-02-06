from DefenderY import DefenderY
import logging


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s]: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO,
    )
    DefenderY = DefenderY('/opt/atp/src/config.yaml')
    DefenderY.run()


