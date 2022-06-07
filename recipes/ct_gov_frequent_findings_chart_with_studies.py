import pandas as pd
from matplotlib import pyplot as plt
from toxhub.dataclass import DataClass
from toxhub.datasource import DataSources
from toxhub.primitiveadaptor import PrimitiveAdaptor
from toxhub.query import QueryBuilder, Fields
from toxhub.toxhub import ToxHub

from credentials import Credentials
from supermarket.ct import CT


def create_list_of_studies_for_compound(compound_name: str, pa: PrimitiveAdaptor):
    q = QueryBuilder().select(DataClass.STUDY).where(Fields.COMPOUND_NAME.eq_(compound_name)).build()
    studies = pa.execute(q, DataSources.CLINCAL_TRIALS)
    df = pd.DataFrame(studies)[['studyIdentifier', 'phase', 'studyType', 'organisation']]
    df.to_csv(f'./output/{compound_name}_studies.tsv', sep='\t')
    print(f'File saved as {compound_name}_ct_studies.tsv in output folder')


def create_chart_most_frequent_findings(compound_name: str, toxhub: ToxHub, severity: str, n: int):
    ct = CT(toxhub)
    findings = ct.findings(compound_name, grouped=True, severity=severity)

    df = pd.DataFrame(findings[:n]).set_index(['finding'])
    df.plot(kind='barh')
    plt.title(f'{compound_name} CT.gov')
    plt.xlabel("Cases")
    plt.ylabel("MedDRA PT")
    plt.gca().invert_yaxis()
    plt.gcf().set_size_inches(10, 7)
    plt.tight_layout()
    plt.savefig(f'./output/{compound_name}.png')
    print(f'File saved as {compound_name}.png in output folder')


def main(compound_name: str, severity: str = 'serious', n: int = 25):
    creds = Credentials()
    toxhub = ToxHub(creds.username, creds.password, creds.env, creds.client_secret)
    print(f"Loading {n} {severity if severity else ''} events for {compound_name}")
    create_chart_most_frequent_findings(compound_name, toxhub, severity, n)
    create_list_of_studies_for_compound(compound_name, toxhub.primitiveAdaptor)


if __name__ == '__main__':
    main('fingolimod')
