from cortex.utils.repository_base import HandlerRecord, RepositoryBase


class SaverRecord(HandlerRecord):
    def format_target_name(self):
        if self._toplevel_prop_name(self.handler).startswith("save_"):
            return self._toplevel_prop_name(self.handler).replace("save_", "").lower()
        else:
            return self._camel_to_snake(self._toplevel_prop_name(self.handler).split("Saver")[0])


class Repository(RepositoryBase):
    @property
    def record_maker(self):
        return SaverRecord

    def specialize_props(self):
        self.prop_name_starts_with('save')
        self.prop_name_ends_with('Saver')

        @self.module_name_filter
        def parser_file_name(x):
            return x.name.endswith('_saver.py') or x.name.startswith('save_')


def get_saver(name):
    rep = Repository.get()
    return rep.get_handler(name)

def has_saver_for(name):
    rep = Repository.get()
    return rep.get_handler(name) is not None


if __name__ == "__main__":
    print(repr(Repository.get().handlers()))
    print(Repository.get().get_handler('pose'))

