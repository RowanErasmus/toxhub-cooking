from toxhub.dataclass import Compound, DataClass, Finding
from toxhub.datasource import DataSources
from toxhub.query import QueryBuilder, Fields
from toxhub.toxhub import ToxHub

from findings import group_by_finding_sum_affected as group


class CT:

    def __init__(self, toxhub: ToxHub):
        self.__pa = toxhub.primitiveAdaptor
        self.__me = DataSources.CLINCAL_TRIALS

    def compounds(self) -> [Compound]:
        q = QueryBuilder().select_all(DataClass.COMPOUND).build()
        compounds = self.__pa.execute(q, self.__me, converter=lambda x: Compound(x))
        compounds.sort(key=lambda c: c.name.lower())
        return compounds

    def findings(self, compound_name: str, grouped: bool = False, severity: str = None):
        builder = QueryBuilder().select(DataClass.FINDING).where(Fields.COMPOUND_NAME.eq_(compound_name))
        if severity:
            q = builder.where(Fields.FINDING_SEVERITY.eq_(severity)).build()
        else:
            q = builder.build()
        findings_raw = self.__pa.execute(q, self.__me, converter=lambda x: Finding(x))
        if grouped:
            return group(findings_raw)
        else:
            return findings_raw
