from query_mongo import get_all_species, look_up_species
from collections import defaultdict
import pandas as pd


class SpeciesTrie:
    def __init__(self, species):
        self.species = species
        self.trie = self._trie_init(self.species)

    def search(self, word: str) -> list:
        trie = self.trie
        word = word.lower()
        results = []
        for w in word:
            if w in trie:
                trie = trie[w]
            else:
                return results

        tasks = [trie]
        while tasks:
            task = tasks.pop()
            for key, value in task.items():
                if key == "end":
                    results.extend(value)
                else:
                    tasks.append(value)
        results.sort(reverse=True)
        return results

    def _trie_init(self, species) -> dict:
        trie = {}
        for sp in species:
            is_ch_not_nan = sp["chinese_common_name"] == sp["chinese_common_name"]
            ans_name = (
                sp["chinese_common_name"]
                if is_ch_not_nan
                else sp["english_common_name"]
            )
            taxon_name = sp["english_common_name"].split(" ")[-1].lower()
            ans = (sp["called_count"], sp["taxon_order"], ans_name)
            if is_ch_not_nan:
                trie = self._insert_trie(trie, sp["chinese_common_name"], ans)
            trie = self._insert_trie(trie, sp["english_common_name"].lower(), ans)
            trie = self._insert_trie(trie, taxon_name, ans)
            for code in sp["code"]:
                trie = self._insert_trie(trie, code.lower(), ans)
        return trie

    def _insert_trie(self, trie, word: str, ans):
        tmp_trie = trie
        for w in word:
            while w not in tmp_trie:
                tmp_trie[w] = {}
            tmp_trie = tmp_trie[w]
        if "end" in tmp_trie:
            tmp_trie["end"].append(ans)
        else:
            tmp_trie["end"] = [ans]
        return trie


class PMOccurrences:
    def __init__(self, bq_occurrences) -> None:
        pass

    # def _group_occurrence_by_id(occurrence: pd.DataFrame):
    #     new_ocurrence = {}
    #     for i, row in occurrence.iterrows():
    #         if row["object_id"] in new_ocurrence:
    #             new_ocurrence[row["object_id"]] =
    #     return

    def _add_common_name(bq_occurrence: pd.DataFrame, order_by="ai", lang="ch"):
        name_col_name = (
            "chinese_common_name" if lang.lower() == "ch" else "english_common_name"
        )
        order_col_name = "taxon_order_by_%s" % order_by
        bq_occurrence[name_col_name] = bq_occurrence.apply(
            lambda df: look_up_species(df[order_col_name])[name_col_name], axis=1
        )
        return bq_occurrence


if __name__ == "__main__":
    trie = SpeciesTrie(get_all_species())
    results = trie.search("sp.")
    for r in results:
        print(r)
