from toxhub.dataclass import Compound, DataClass
from toxhub.datasource import DataSources
from toxhub.query import QueryBuilder, Fields, ComparisonOperator
from toxhub.toxhub import ToxHub


class ETox:

    def __init__(self, toxhub: ToxHub):
        self.__pa = toxhub.primitiveAdaptor
        self.__me = DataSources.ETOX

    def compounds(self) -> [Compound]:
        q = QueryBuilder().select_all(DataClass.COMPOUND).build()
        compounds = self.__pa.execute(q, self.__me, converter=lambda x: Compound(x))
        compounds.sort(key=lambda c: c.name.lower())
        return compounds

    def findings(self, inchikey: str, finding_type: str = None, exclude_control: bool = True):
        builder = QueryBuilder().select(DataClass.FINDING).where(Fields.COMPOUND_INCHIKEY.eq_(inchikey))
        if finding_type:
            builder = builder.and_(Fields.FINDING_TYPE.eq_(finding_type))
        if exclude_control:
            builder = builder.and_(Fields.FINDING_DOSE.custom_operator(["0", "0.0"], ComparisonOperator.NOT_IN))
        q = builder.build()
        return self.__pa.execute(q, self.__me)
