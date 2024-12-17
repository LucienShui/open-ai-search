# https://blog.csdn.net/qq_36606793/article/details/118523699
def pytest_collection_modifyitems(items):  # noqa
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")  # noqa
