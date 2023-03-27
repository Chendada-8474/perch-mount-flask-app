from query_mongo import get_species
import numpy as np


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
            ans_name = (
                sp["chinese_common_name"]
                if np.isnan(sp["chinese_common_name"])
                else sp["english_common_name"]
            )
            ans = (sp["called_count"], sp["taxon_order"], ans_name)
            trie = self._insert_trie(trie, sp["chinese_common_name"], ans)
            trie = self._insert_trie(trie, sp["english_common_name"].lower(), ans)
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


if __name__ == "__main__":
    trie = SpeciesTrie(get_species())
    results = trie.search("black")
    for r in results:
        print(r)
