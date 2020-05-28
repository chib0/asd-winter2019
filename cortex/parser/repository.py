
from cortex.utils.repository_base import RepositoryBase, HandlerRecord


class ParserRecord(HandlerRecord):
    def __init__(self, prop):
        super().__init__(prop)

    def format_target_name(self):
        if self._toplevel_prop_name(self.handler).startswith("parse_"):
            return self._camel_to_snake(self._toplevel_prop_name(self.handler).replace("parse_", "").lower())
        else:
            return self._camel_to_snake(self._toplevel_prop_name(self.handler).split("Parser")[0])

    def __str__(self):
        return f"{self.__class__.__name__} for {self.target}"

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.target} using {self.handler} >"


class Repository(RepositoryBase):
    @property
    def record_maker(self):
        return ParserRecord

    def specialize_props(self):
        self.prop_name_starts_with('parse')
        self.prop_name_ends_with('Parser')

        @self.module_name_filter
        def parser_file_name(x):
            return x.name.endswith('_parser.py') or x.name.startswith('parse_')


def get_parser(name):
    rep = Repository.get()
    return rep.get_handler(name)

def has_parser_for(name):
    rep = Repository.get()
    return rep.get_handler(name) is not None


if __name__ == "__main__":
    print(repr(Repository.get().handlers()))
    print(Repository.get().get_handler('pose'))

