import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from toxhub.dataclass import DataClass
from toxhub.datasource import DataSources
from toxhub.query import QueryBuilder, Fields
from toxhub.toxhub import ToxHub

from credentials import Credentials
from supermarket.etox import ETox


def main():
    # Authentication
    creds = Credentials()
    toxhub = ToxHub(creds.username, creds.password, creds.env, creds.client_secret)
    etox = ETox(toxhub)

    # Compound name to standard name and structure using chemistry service
    chem_serv = toxhub.chemistryService
    omeprazole = chem_serv.compound_by_name('Omeprazole')
    print(omeprazole)

    # Similar compounds from similarity service
    sim_compounds = toxhub.similarityService.get(omeprazole.smiles, DataSources.MEDLINE)
    for compound in sim_compounds:
        print(compound)

    # Standardize compounds to get inchikeys which will be used to search databases
    standardized_compounds = map(lambda c: chem_serv.compound_by_name(c.name), sim_compounds)
    for compound in standardized_compounds:
        print(f'{compound.name} {compound.inchikey}')

    # Get all findings for each compound from various data sources
    pa = toxhub.primitiveAdaptor
    data_sources = [DataSources.ETOX, DataSources.MEDLINE, DataSources.FAERS, DataSources.CLINCAL_TRIALS,
                    DataSources.DAILYMED]
    for source in data_sources:
        compound_soc_count_list = []
        for compound in standardized_compounds:
            # Get all the findings for inchikey
            query = QueryBuilder().select(DataClass.FINDING).where(
                Fields.COMPOUND_INCHIKEY.eq_(compound.inchikey)).build()
            findings = etox.findings(compound.inchikey, 'Histopathology') if source == DataSources.ETOX else pa.execute(
                query, source)
            print(f'{len(findings)} findings for {compound.name} in {source}')

            # Translate findings to socs
            socs_map = toxhub.semanticService.socs_for_findings(findings)
            socs = []
            for f in socs_map:
                mappings = f['mapping']
                for mapping in mappings:
                    socs.append(str(mapping['conceptName'])[0:25])
            # Count occurrences for each soc
            for soc_name in set(socs):
                compound_soc_count_list.append(
                    {'compound': compound.name, 'soc': soc_name, 'count': socs.count(soc_name)})

        # Put the list in a data frame and show the heatmap
        df = pd.DataFrame(compound_soc_count_list).pivot('soc', 'compound', values='count')
        plt.title(source.__str__())
        sns.heatmap(df, linewidth=1, cmap="YlGnBu", annot=True, fmt=".0f")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
