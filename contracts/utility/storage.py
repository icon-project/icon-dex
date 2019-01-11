from iconservice import IconScoreDatabase, VarDB


class Storage:
    """
    Wrapper class of icon container dbs.

    field_info = list of tuple ('field name', type of container db, value type)
    e.g.)
        FIELDS = [
            ('smart_token_address', VarDB, Address),
            ('registry', VarDB, Address),
            ('prev_registry', VarDB, Address),
            ('conversion_whitelist', VarDB, Address),
            ('connector_tokens', ArrayDB, Address),
            ('total_connector_weight', VarDB, int),
            ('max_conversion_fee', VarDB, int),
            ('conversion_fee', VarDB, int),
            ('conversions_enabled', VarDB, bool)
        ]
    """

    def __init__(self, db: IconScoreDatabase):
        self._db = db

    def add_fields(self, field_infos):
        """
        Add fields to this object

        :param field_infos: list of tuple `field info`
        """
        for name, db_class, value_type in field_infos:
            db = db_class(name, self._db, value_type=value_type)
            setattr(self, f'_{name}', db)

    def __setattr__(self, item, value):
        shadow = f'_{item}'
        attr = getattr(self, shadow, None)
        if isinstance(attr, VarDB):
            attr.set(value)
        else:
            super().__setattr__(item, value)

    def __getattribute__(self, item):
        if not item.startswith('_'):
            shadow = f'_{item}'
            if hasattr(self, shadow):
                # If the shadow object of given attribute exists returns it
                # and if it is instance of VarDB, returns real value
                attr = getattr(self, shadow)
                return attr.get() if isinstance(attr, VarDB) else attr
        return super().__getattribute__(item)
