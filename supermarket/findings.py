import itertools

from toxhub.dataclass import Finding


def group_by_finding_sum_affected(findings: [Finding], filters=lambda f: True):
    findings.sort(key=lambda x: x.name)
    grouped = []
    for f, r in itertools.groupby(findings, lambda x: x.name):
        if filters(f):
            grouped.append({'finding': f, 'frequency': sum(v.frequency.affected for v in r)})
    grouped.sort(key=lambda f: f['frequency'], reverse=True)
    return grouped
