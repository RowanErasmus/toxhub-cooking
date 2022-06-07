from toxhub.dataclass import DataClass
from toxhub.datasource import DataSource
from toxhub.query import QueryBuilder
from toxhub.toxhub import ToxHub

from credentials import Credentials


def local_pa():
    creds = Credentials()
    toxhub = ToxHub(creds.username, creds.password, creds.env, creds.client_secret)
    pa = toxhub.primitiveAdaptor
    # Override base url
    pa.url = 'http://localhost:9012'
    return pa


def main():
    pa = local_pa()
    # set correct path, chemical space is irrelevant
    source = DataSource('/primitive-adaptor/v1', 'localpa')
    q = QueryBuilder().select_all(DataClass.COMPOUND).build()
    compounds = pa.execute(q, source)
    print(compounds)


if __name__ == "__main__":
    main()
