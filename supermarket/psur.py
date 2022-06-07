from toxhub.dataclass import Compound, DataClass, Finding
from toxhub.datasource import DataSources
from toxhub.primitiveadaptor import PrimitiveAdaptor
from toxhub.query import QueryBuilder, Fields


class PSUR:

    def __init__(self, pa: PrimitiveAdaptor):
        self.__pa = pa
        self.__me = DataSources.PSUR

    def compounds(self) -> [Compound]:
        q = QueryBuilder().select_all(DataClass.COMPOUND).build()
        compounds = self.__pa.execute(q, self.__me, converter=lambda x: Compound(x))
        compounds.sort(key=lambda c: c.name.lower())
        return compounds

    def findings(self, compound_id: int, finding_types: [str] = None) -> [Finding]:
        builder = QueryBuilder().select(DataClass.FINDING).where(Fields.FINDING_COMPOUND_ID.eq_(compound_id))
        if finding_types:
            q = builder.and_(Fields.FINDING_TYPE.in_(finding_types)).build()
        else:
            q = builder.build()
        return self.__pa.execute(q, DataSources.PSUR, converter=lambda x: Finding(x))
