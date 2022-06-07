from datetime import datetime

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import DataFrame
from toxhub.dataclass import Compound, DataClass, Finding, Study
from toxhub.datasource import DataSources
from toxhub.primitiveadaptor import PrimitiveAdaptor
from toxhub.query import QueryBuilder, Fields
from toxhub.toxhub import ToxHub

from credentials import Credentials
from supermarket.findings import group_by_finding_sum_affected as group
from supermarket.psur import PSUR


def psur_last_updated(findings: [Finding], pa: PrimitiveAdaptor) -> datetime:
    study_ids = set(map(lambda f: f.studyId, findings))
    q = QueryBuilder().select(DataClass.STUDY).where(Fields.STUDY_ID.in_(study_ids)).build()
    study_dates = pa.execute(q, DataSources.PSUR, lambda x: datetime.fromisoformat(Study(x).modified))
    study_dates.sort(reverse=True)
    return study_dates[0]


def faers_findings_by_compound(c: Compound, pa: PrimitiveAdaptor) -> [Finding]:
    q = QueryBuilder().select(DataClass.FINDING).where(Fields.COMPOUND_INCHIKEY.eq_(c.inchikey)).build()
    findings = pa.execute(q, DataSources.FAERS, lambda x: Finding(x))
    if len(findings) == 0:
        print(f'Checking FAERS by name for {c.name}')
        q = QueryBuilder().select(DataClass.FINDING).where(Fields.COMPOUND_NAME.eq_(c.name)).build()
        findings = pa.execute(q, DataSources.FAERS, lambda x: Finding(x))
    return group(findings)


def find_frequent_findings(findings, amount: int = 15, threshold: int = 3) -> [str]:
    findings.sort(key=lambda x: x['frequency'], reverse=True)
    most_frequent = []
    for f in findings[:amount]:
        if f['frequency'] > threshold:
            most_frequent.append(f['finding'])
    return most_frequent


def create_items(findings, most_frequent_findings, source: str):
    items = []
    for f in findings:
        if f['finding'] in most_frequent_findings:
            items.append({'source': source, 'finding': f['finding'], 'count': int(f['frequency'])})
    return items


def build_frame(psur_findings, faers_findings, most_frequent_findings, date: datetime):
    items = []
    items.extend(create_items(psur_findings, most_frequent_findings, f"PSUR {date.strftime('%m-%d-%Y')}"))
    items.extend(create_items(faers_findings, most_frequent_findings, 'FAERS'))
    df = pd.DataFrame(items)
    return df.pivot('finding', 'source', values='count')


def visualize(df: DataFrame, title: str, show: bool = True, save: bool = False):
    f, ax = plt.subplots()
    ax.set_title(title)
    sns.heatmap(df, linewidth=1, cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
    plt.tight_layout()
    if save:
        plt.savefig(f'./{title}.png')
    if show:
        plt.show()
    plt.close()


def main():
    creds = Credentials()
    toxhub = ToxHub(creds.username, creds.password, creds.env, creds.client_secret)
    pa = toxhub.primitiveAdaptor
    psur = PSUR(pa)
    compounds = psur.compounds()

    i = 0
    for c in compounds:
        i += 1
        print(f'{c.name} ({i} out of {len(compounds)})')
        faers_findings = faers_findings_by_compound(c, pa)

        if len(faers_findings) == 0:
            print(f'Nothing found in FAERS for {c.name} skipping')
            continue

        psur_findings_raw = psur.findings(c.id, finding_types=['sr_all'])
        psur_date = psur_last_updated(psur_findings_raw, pa)
        psur_findings = group(psur_findings_raw, filters=lambda f: 'SOC Sub' not in f and 'Total' != f)

        most_frequent_findings = []
        most_frequent_findings.extend(find_frequent_findings(psur_findings))
        most_frequent_findings.extend(find_frequent_findings(faers_findings))

        df = build_frame(psur_findings, faers_findings, most_frequent_findings, psur_date)
        visualize(df, c.name.lower())


if __name__ == '__main__':
    main()
