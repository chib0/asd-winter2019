from cortex.utils.repository_base import RepositoryBase


class Repository(RepositoryBase):
    def specialize_props(self):
        @self.module_name_filter
        def db_name(x):
            return x.name.endswith('_database.py') or x.name.endswith('_db.py') or x.name.endswith("_db_driver")

    @property
    def record_maker(self):
        return lambda x: x


def get_database(url):
    repo = Repository.get()
    for i in repo.modules():
        db = i.get_database(url)
        if db:
            return db
    return None
