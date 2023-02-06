import os

print "__file__ = {} \n".format(os.path.dirname(__file__))

print os.getcwd()
for element in sorted(os.listdir(os.getcwd())):
    print "> `{}`".format(element)
