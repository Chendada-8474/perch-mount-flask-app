import datetime
import shutil
from pathlib import Path
from config import *
from query_mongo import get_all_species, look_up_species, get_path_by_object_id


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
        self.occurrence = self._group_occurrence_by_id(bq_occurrences)
        self._add_path()
        self._add_common_name(taxon_order_by="ai", lang="chinese")
        self._add_common_name(taxon_order_by="human", lang="chinese")

    def _group_occurrence_by_id(self, occurrence):
        new_ocurrence = {}
        for row in occurrence:
            medium, individual = self._split_individual_medium(dict(row))
            object_id = medium.pop("object_id")
            if object_id not in new_ocurrence:
                new_ocurrence[object_id] = medium
                new_ocurrence[object_id]["individual"] = [individual]
            else:
                new_ocurrence[object_id]["individual"].append(individual)
        return new_ocurrence

    def _split_individual_medium(self, row) -> dict:
        individual = row
        medium = {}
        for col_name in MEDIUM_COL_NAME:
            medium[col_name] = individual.pop(col_name)
        return medium, individual

    def _add_path(self):
        for object_id in self.occurrence.keys():
            self.occurrence[object_id]["path"] = get_path_by_object_id(object_id)

    def _add_common_name(self, taxon_order_by="ai", lang="chinese"):
        name_col_name = "%s_common_name" % lang
        taxon_order_col_name = "taxon_order_by_%s" % taxon_order_by
        new_col_name = "%s_%s" % (name_col_name, taxon_order_by)
        for medium in self.occurrence.values():
            for individual in medium["individual"]:
                individual[new_col_name] = (
                    look_up_species(individual[taxon_order_col_name])[name_col_name]
                    if individual[taxon_order_col_name]
                    else None
                )


class PMRawMedia:
    def __init__(self, bq_raw_media) -> None:
        self.raw_media = self._init_pm_raw_media(bq_raw_media)
        self._add_path()

    def __len__(self):
        return len(self.raw_media)

    def __getitem__(self, index):
        return self.raw_media[index]

    def _init_pm_raw_media(self, bq_raw_media):
        rows = []
        for row in bq_raw_media:
            row = dict(row)
            row["medium_date"] = row["medium_date"].strftime(DATE_FROMAT)
            row["medium_datetime"] = row["medium_datetime"].strftime(DATETIME_FROMAT)
            rows.append(row)
        return rows

    def _add_path(self):
        for medium in self.raw_media:
            medium["path"] = get_path_by_object_id(medium["object_id"])


def move_file_to_empty_dir_by_ids(object_ids: list):
    for object_id in object_ids:
        ori_path = get_path_by_object_id(object_id)
        des_dir = Path(EMPTY_DES_DIR)
        ori_path = Path(ori_path)
        des_dir.mkdir(parents=True, exist_ok=True)
        file_name = ori_path.name
        shutil.move(ori_path, des_dir / file_name)


if __name__ == "__main__":
    test = PMOccurrences({})
    print(
        test._extract_individual_info(
            {
                "taxon_order_by_ai": 7575,
                "taxon_order_by_human": None,
                "medium_datetime": datetime.datetime(
                    2022, 4, 8, 13, 39, 30, tzinfo=datetime.timezone.utc
                ),
                "medium_date": datetime.date(2022, 4, 8),
                "perch_mount_id": 3,
                "perch_mount_name": "土庫南側",
                "main_behavior_ch": None,
                "main_behavior_eng": None,
                "secondary_behavior_ch": None,
                "secondary_behavior_eng": None,
                "prey_ch": None,
                "prey_eng": None,
                "adult": None,
                "tagged": None,
                "transmitter": None,
                "xmin": 0.1822,
                "xmax": 0.5762,
                "ymin": 0.3799,
                "ymax": 0.825,
                "featured": None,
                "object_id": "64168e9a697b9520481d2bd2",
            }
        )
    )
