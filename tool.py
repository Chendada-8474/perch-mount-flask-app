import os
import datetime
import shutil
from datetime import datetime
from collections import defaultdict
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

        results = list(set(results))
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


class ReviewIndividual:
    def __init__(self, individual_info) -> None:
        self.__dict__.update(individual_info)
        self._add_common_name()

    def _add_common_name(self, taxon_order_by="ai", lang="chinese"):
        name_col_name = "%s_common_name" % lang
        taxon_order_col_name = "taxon_order_by_%s" % taxon_order_by
        new_col_name = "%s_%s" % (name_col_name, taxon_order_by)
        new_name = {}
        new_name[new_col_name] = (
            look_up_species(self.__dict__[taxon_order_col_name])[name_col_name]
            if self.__dict__[taxon_order_col_name]
            else None
        )
        self.__dict__.update(new_name)


class ReviewMedium:
    def __init__(self, medium_info: dict) -> None:
        self.__dict__.update(medium_info)
        self._path = self._get_path(self.object_id)
        self.file_name = os.path.basename(self.path)
        self.individuals = self._objectirize_individual(self.individuals)

    def _get_path(self, object_id):
        return get_path_by_object_id(object_id)

    def _strftime(self, medium_datetime, medium_date):
        self.medium_datetime = medium_datetime.strftime(DATE_FROMAT)
        self.medium_date = medium_date.strftime(DATE_FROMAT)

    def _objectirize_individual(self, individual):
        return [ReviewIndividual(individual) for individual in self.individuals]

    @property
    def path(self):
        return self._path.replace("\\", "/").replace("#", "%23")

    @property
    def is_image(self):
        _, ext = os.path.splitext(self.path)
        return ext[1:].lower() in IMAGE_EXTENSIONS


class ReviewMedia:
    def __init__(self, orm_occurrences) -> None:
        self.orm_occurrences = orm_occurrences
        self._media = self._dictirize(orm_occurrences)
        self._media_objects = self._objectirize(self._media)
        # self._add_path()
        # self._strftime()
        # self._add_common_name(taxon_order_by="ai", lang="chinese")

    def __len__(self):
        return len(self._media)

    def __getitem__(self, index):
        return self._media_objects[index]

    def _dictirize(self, occurrences):
        new_occurrence = {}
        for row in occurrences:
            row_dict = row.__dict__.copy()
            row_dict.pop("_sa_instance_state")
            row_dict.pop("detected_medium_id")
            row_dict.pop("detected_datetime")
            medium_info, individual = self._split_individual_medium(row_dict)
            object_id = medium_info["object_id"]
            if object_id in new_occurrence:
                new_occurrence[object_id]["individuals"].append(individual)
            else:
                new_occurrence[object_id] = medium_info
                new_occurrence[object_id]["individuals"] = [individual]

        return new_occurrence

    def _objectirize(self, media):
        return [ReviewMedium(content) for content in media.values()]

    def _strftime(self):
        for object_id, occurrence in self._media.items():
            self._media[object_id]["medium_date"] = occurrence["medium_date"].strftime(
                DATE_FROMAT
            )
            self._media[object_id]["medium_datetime"] = occurrence[
                "medium_datetime"
            ].strftime(DATETIME_FROMAT)

    def _split_individual_medium(self, row) -> dict:
        individual = row
        medium = {}
        for col_name in MEDIUM_COL_NAME:
            medium[col_name] = individual.pop(col_name)
        return medium, individual

    def _add_path(self):
        for object_id in self._media.keys():
            self._media[object_id]["path"] = get_path_by_object_id(object_id)

    def _add_common_name(self, taxon_order_by="ai", lang="chinese"):
        name_col_name = "%s_common_name" % lang
        taxon_order_col_name = "taxon_order_by_%s" % taxon_order_by
        new_col_name = "%s_%s" % (name_col_name, taxon_order_by)
        for medium in self._media.values():
            for individual in medium["individuals"]:
                individual[new_col_name] = (
                    look_up_species(individual[taxon_order_col_name])[name_col_name]
                    if individual[taxon_order_col_name]
                    else None
                )


# class PMRawMedia:
#     def __init__(self, bq_raw_media) -> None:
#         self.raw_media = self._init_pm_raw_media(bq_raw_media)
#         self._add_path()

#     def __len__(self):
#         return len(self.raw_media)

#     def __getitem__(self, index):
#         return self.raw_media[index]

#     def _init_pm_raw_media(self, bq_raw_media):
#         rows = []
#         for row in bq_raw_media:
#             row = dict(row)
#             row["medium_date"] = row["medium_date"].strftime(DATE_FROMAT)
#             row["medium_datetime"] = row["medium_datetime"].strftime(DATETIME_FROMAT)
#             rows.append(row)
#         return rows

#     def _add_path(self):
#         for medium in self.raw_media:
#             medium["path"] = get_path_by_object_id(medium["object_id"])


class EmptyCheckMedium:
    def __init__(self, orm_object):
        self.orm_object = orm_object

    @property
    def json(self):
        d = self.orm_object.__dict__
        d["medium_date"] = d["medium_date"].strftime(DATE_FROMAT)
        d["medium_datetime"] = d["medium_datetime"].strftime(DATETIME_FROMAT)
        d["path"] = get_path_by_object_id(d["object_id"])
        d.pop("_sa_instance_state")
        return d


class EmptyCheckMedia:
    def __init__(self, empty_media) -> None:
        self.empty_media = empty_media
        self.media = self._init_pm_raw_media(empty_media)

    def __len__(self):
        return len(self.media)

    def __getitem__(self, index):
        return self.media[index]

    def _init_pm_raw_media(self, empty_media):
        rows = []
        for row in empty_media:
            rows.append(EmptyCheckMedium(row))
        return rows

    @property
    def json(self):
        return [medium.json for medium in self]


class VariableDictionary:
    def __init__(self, all_species, all_prey, all_behavior, all_event):
        self.all_species = all_species
        self.all_prey = all_prey
        self.all_behavior = all_behavior
        self.all_event = all_event
        self.from_ch = self._name_to_taxon_order("chinese_common_name")
        self.from_eng = self._name_to_taxon_order("english_common_name")
        self.prey_from_id = self._id_to_prey_name()
        self.behavior_from_id = self._id_to_behavior_name()
        self.event_from_id = self._id_to_event_name()

    def _name_to_taxon_order(self, field):
        return {species[field]: species["taxon_order"] for species in self.all_species}

    def _id_to_behavior_name(self):
        return {
            behavior.behavior_id: {
                "behavior_ch_name": behavior.behavior_ch_name,
                "behavior_eng_name": behavior.behavior_eng_name,
            }
            for behavior in self.all_behavior
        }

    def _id_to_prey_name(self):
        return {
            prey.prey_id: {
                "prey_ch_name": prey.prey_ch_name,
                "prey_eng_name": prey.prey_eng_name,
            }
            for prey in self.all_prey
        }

    def _id_to_event_name(self):
        return {
            event.event_id: {
                "event_ch_name": event.event_ch_name,
                "event_eng_name": event.event_eng_name,
            }
            for event in self.all_event
        }

    def has_common_name(self, common_name, lang="ch"):
        return (
            common_name in self.from_ch
            if lang == "ch"
            else common_name in self.from_eng
        )

    def query_taxon_order(self, common_name, lang="ch"):
        if lang == "ch":
            return self.from_ch[common_name]
        elif lang == "eng":
            return self.from_eng[common_name]

    def query_prey_name(self, prey_id, lang="ch"):
        if lang == "ch":
            return self.prey_from_id[prey_id]["prey_ch_name"]
        elif lang == "eng":
            return self.prey_from_id[prey_id]["prey_eng_name"]

    def query_behavior_name(self, behavior_id, lang="ch"):
        if lang == "ch":
            return self.behavior_from_id[behavior_id]["behavior_ch_name"]
        elif lang == "eng":
            return self.behavior_from_id[behavior_id]["behavior_eng_name"]

    def query_event_name(self, event_id, lang="ch"):
        if lang == "ch":
            return self.event_from_id[event_id]["event_ch_name"]
        elif lang == "eng":
            return self.event_from_id[event_id]["event_eng_name"]


def move_file_to_empty_dir_by_ids(object_ids: list) -> list:
    check_date = datetime.now().strftime(DATE_FROMAT)
    des_dir = Path(EMPTY_DES_DIR) / Path(check_date)
    des_dir.mkdir(parents=True, exist_ok=True)
    errors = []
    for object_id in object_ids:
        try:
            ori_path = get_path_by_object_id(object_id)
            ori_path = Path(ori_path)
            file_name = ori_path.name
            shutil.move(ori_path, des_dir / file_name)
        except:
            errors.append(object_id)
    return errors


def create_empty_move_tasks(object_ids):
    tasks_dir = "D:/python/perch-mount-flask-app/empty-tasks"
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    task_path = "%s/%s.txt" % (tasks_dir, now)
    with open(task_path, "w") as t:
        t.writelines(get_path_by_object_id(o) for o in object_ids)


if __name__ == "__main__":
    import query_mysql

    data = query_mysql.get_detected_occurrences("九地樹林")
    # for d in data:
    #     print(d.__dict__)
    data = ReviewMedia(data)
    for d in data:
        print(d.__dict__)
