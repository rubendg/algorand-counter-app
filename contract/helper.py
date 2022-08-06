from pyteal import App, Expr, Bytes


class GlobalVar:
    """Makes global var manipulation a bit easier on the eye"""

    def __init__(self, key: str):
        self.key = Bytes(key)

    def set(self, v: Expr):
        return App.globalPut(self.key, v)

    def delete(self):
        return App.globalDel(self.key)

    def get(self):
        return App.globalGet(self.key)


class Globals:
    def __getitem__(self, item: str):
        return GlobalVar(item)


global_bindings = Globals()
