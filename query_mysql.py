import os
import yaml
from config import *
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, select, and_, or_, func, desc, distinct, tuple_
from sqlalchemy.orm import scoped_session, sessionmaker, aliased, declarative_base
from contextlib import contextmanager

CONFIG_PATH = Path(__file__).parent / "connect_config/mysql_config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as config:
    mysql_config = yaml.safe_load(config)

MYSQL_PW = mysql_config["password"]
MYSQL_IP = mysql_config["ip"]
MYSQL_DB_NAME = mysql_config["database"]

engine = create_engine(
    "mysql+pymysql://root:%s@%s/%s" % (MYSQL_PW, MYSQL_IP, MYSQL_DB_NAME),
    pool_recycle=3600,
    pool_pre_ping=True,
    isolation_level="AUTOCOMMIT",
    pool_size=20,
    max_overflow=0,
)

Base = declarative_base()
Base.metadata.reflect(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


db_session = scoped_session(sessionmaker(bind=engine))


class CameraORM(Base):
    __table__ = Base.metadata.tables["camera"]


class BehaviourORM(Base):
    __table__ = Base.metadata.tables["behavior"]


class MemberORM(Base):
    __table__ = Base.metadata.tables["member"]


class MountTypeORM(Base):
    __table__ = Base.metadata.tables["mount_type"]


class ProjectORM(Base):
    __table__ = Base.metadata.tables["project"]


class PositionORM(Base):
    __table__ = Base.metadata.tables["position"]


class PerchMountORM(Base):
    __table__ = Base.metadata.tables["perch_mount"]


class PerchMountProjectORM(Base):
    __table__ = Base.metadata.tables["perch_mount_project"]


class HabitatORM(Base):
    __table__ = Base.metadata.tables["habitat"]


class PreyORM(Base):
    __table__ = Base.metadata.tables["prey"]


class EventORM(Base):
    __table__ = Base.metadata.tables["event"]


class EmptyMediumORM(Base):
    __table__ = Base.metadata.tables["empty_medium"]


class DetectedMediumORM(Base):
    __table__ = Base.metadata.tables["detected_medium"]


class FeatureMediumORM(Base):
    __table__ = Base.metadata.tables["feature_medium"]


def is_media_reviewed(object_ids: list) -> bool:
    with session_scope() as db_session:
        query = (
            db_session.query(DetectedMediumORM.reviewed)
            .filter(DetectedMediumORM.object_id.in_(object_ids))
            .all()
        )
    return any(q[0] for q in query)


def get_users_login_info():
    with session_scope() as db_session:
        querys = db_session.query(MemberORM).all()
        db_session.expunge_all()

    users = {}
    for user in querys:
        users[user.user_name] = {
            "phone_number": user.phone_number,
            "member_id": user.member_id,
            "admin": user.admin == 1,
            "super_admin": user.super_admin == 1,
        }
    return users


def get_full_table(table_orm):
    with session_scope() as db_session:
        table = db_session.query(table_orm).all()
        db_session.expunge_all()
    return table


def get_perch_mount_names():
    with session_scope() as db_session:
        perch_mount_names = db_session.query(PerchMountORM.perch_mount_name).all()
        db_session.expunge_all()
    return [name[0] for name in perch_mount_names]


def get_perch_mounts():
    with session_scope() as db_session:
        perch_mount = (
            db_session.query(PerchMountORM, ProjectORM, HabitatORM)
            .join(HabitatORM, PerchMountORM.habitat_id == HabitatORM.habitat_id)
            .join(ProjectORM, PerchMountORM.project_id == ProjectORM.project_id)
            .all()
        )
        db_session.expunge_all()
    return perch_mount


def get_behaviors():
    with session_scope() as db_session:
        behaviors = db_session.query(BehaviourORM).all()
        db_session.expunge_all()
    return behaviors


def get_members():
    with session_scope() as db_session:
        members = (
            db_session.query(MemberORM, PositionORM)
            .join(PositionORM, PositionORM.position_id == MemberORM.position_id)
            .all()
        )
        db_session.expunge_all()
    return members


def get_cameras():
    with session_scope() as db_session:
        cameras = db_session.query(CameraORM).order_by(CameraORM.camera_id).all()
        db_session.expunge_all()
    return cameras


def get_preys():
    with session_scope() as db_session:
        preys = db_session.query(PreyORM).all()
        db_session.expunge_all()
    return preys


def get_positions():
    with session_scope() as db_session:
        positions = db_session.query(PositionORM).all()
        db_session.expunge_all()
    return positions


def get_habitats():
    with session_scope() as db_session:
        habitats = db_session.query(HabitatORM).all()
        db_session.expunge_all()
    return habitats


def get_projects():
    with session_scope() as db_session:
        project = db_session.query(ProjectORM).all()
        db_session.expunge_all()
    return project


def get_events():
    with session_scope() as db_session:
        events = db_session.query(EventORM).all()
        db_session.expunge_all()
    return events


def get_habitat_by_id(habitat_id):
    with session_scope() as db_session:
        habitat = (
            db_session.query(HabitatORM)
            .filter(HabitatORM.habitat_id == habitat_id)
            .one()
        )
        db_session.expunge_all()
    return habitat


def get_id_by_perch_mount_name(perch_mount_name: str):
    with session_scope() as db_session:
        perch_mount_id = (
            db_session.query(PerchMountORM.perch_mount_id)
            .filter(PerchMountORM.perch_mount_name == perch_mount_name)
            .one()
        )
        db_session.expunge_all()
    return perch_mount_id[0]


def get_project_by_id(project_id):
    with session_scope() as db_session:
        project = (
            db_session.query(ProjectORM)
            .filter(ProjectORM.project_id == project_id)
            .one()
        )
        db_session.expunge_all()
    return project


def get_empty_media(
    perch_mount_name,
    start_datetime="2000-01-01 00:00:00",
    end_datetime=DATETIME_NOW,
    limit=500,
):
    with session_scope() as db_session:
        media = (
            db_session.query(EmptyMediumORM)
            .filter(
                and_(
                    EmptyMediumORM.perch_mount_name == perch_mount_name,
                    EmptyMediumORM.medium_datetime >= start_datetime,
                    EmptyMediumORM.medium_datetime <= end_datetime,
                    EmptyMediumORM.empty_checked == 0,
                )
            )
            .order_by(EmptyMediumORM.medium_datetime)
            .limit(limit)
        )
        media.with_entities(
            EmptyMediumORM.perch_mount_name,
            EmptyMediumORM.perch_mount_id,
            EmptyMediumORM.medium_datetime,
            EmptyMediumORM.medium_date,
            EmptyMediumORM.object_id,
        )
        db_session.expunge_all()
    return media


def get_detected_occurrences(
    perch_mount_name,
    start_datetime="2000-01-01 00:00:00",
    end_datetime=DATETIME_NOW,
    limit=500,
):
    start_datetime = datetime.strptime(start_datetime, DATETIME_FROMAT)
    end_datetime = datetime.strptime(end_datetime, DATETIME_FROMAT)
    with session_scope() as db_session:
        occourrences = (
            db_session.query(DetectedMediumORM)
            .filter(
                and_(
                    DetectedMediumORM.reviewed == 0,
                    DetectedMediumORM.medium_datetime >= start_datetime,
                    DetectedMediumORM.medium_datetime <= end_datetime,
                    DetectedMediumORM.perch_mount_name == perch_mount_name,
                )
            )
            .order_by(DetectedMediumORM.medium_datetime)
            .limit(limit)
            .all()
        )
        db_session.expunge_all()

    return occourrences


def get_date_pending_detected_media_by_id(perch_mount_id):
    with session_scope() as db_session:
        meida = db_session.execute(
            select(
                DetectedMediumORM.perch_mount_name,
                func.date(DetectedMediumORM.medium_datetime).label("medium_date"),
                func.count().label("pending_count"),
            )
            .filter(
                DetectedMediumORM.reviewed == 0,
                DetectedMediumORM.perch_mount_id == perch_mount_id,
            )
            .group_by(
                DetectedMediumORM.perch_mount_name,
                func.date(DetectedMediumORM.medium_datetime),
            )
            .order_by(func.date(DetectedMediumORM.medium_datetime))
        )
        db_session.expunge_all()
    return meida


def get_date_pending_empty_media_by_id(perch_mount_id):
    with session_scope() as db_session:
        meida = db_session.execute(
            select(
                EmptyMediumORM.perch_mount_name,
                func.date(EmptyMediumORM.medium_datetime).label("medium_date"),
                func.count().label("pending_count"),
            )
            .filter(
                EmptyMediumORM.empty_checked == 0,
                EmptyMediumORM.perch_mount_id == perch_mount_id,
            )
            .group_by(
                func.date(EmptyMediumORM.medium_datetime),
                EmptyMediumORM.perch_mount_name,
            )
            .order_by(func.date(EmptyMediumORM.medium_datetime))
        )
        db_session.expunge_all()
    return meida


def get_pending_perch_mounts():
    empty_query = (
        select(
            EmptyMediumORM.perch_mount_name,
            func.count().label("empty_count"),
        )
        .filter(EmptyMediumORM.empty_checked == 0)
        .group_by(EmptyMediumORM.perch_mount_name)
    ).subquery()

    detected_query = (
        select(
            DetectedMediumORM.perch_mount_name,
            func.count().label("detected_count"),
        )
        .filter(DetectedMediumORM.reviewed == 0)
        .group_by(DetectedMediumORM.perch_mount_name)
    ).subquery()

    with session_scope() as db_session:
        results = db_session.execute(
            select(
                PerchMountORM.perch_mount_name,
                detected_query.c.detected_count,
                empty_query.c.empty_count,
                ProjectORM.project_name,
                ProjectORM.project_id,
                PerchMountORM.perch_mount_id,
                PerchMountORM.latest_note,
                PerchMountORM.claim_by,
                PerchMountORM.is_priority,
                MemberORM.first_name,
                MemberORM.user_name,
            )
            .outerjoin(
                detected_query,
                detected_query.c.perch_mount_name == PerchMountORM.perch_mount_name,
            )
            .outerjoin(
                empty_query,
                empty_query.c.perch_mount_name == PerchMountORM.perch_mount_name,
            )
            .join(ProjectORM, ProjectORM.project_id == PerchMountORM.project_id)
            .join(
                MemberORM, PerchMountORM.claim_by == MemberORM.member_id, isouter=True
            )
            .filter(
                or_(
                    detected_query.c.detected_count != 0,
                    empty_query.c.empty_count != 0,
                    PerchMountORM.claim_by,
                    PerchMountORM.is_priority,
                )
            )
        )
    return results


def get_featured_species():
    with session_scope() as db_session:
        species = db_session.query(FeatureMediumORM.species).all()
        db_session.expunge_all()
    return list(set(sp[0] for sp in species))


def get_featured_behaviors():
    with session_scope() as db_session:
        behaviors = db_session.query(FeatureMediumORM.behavior).all()
        db_session.expunge_all()
    return list(set(b[0] for b in behaviors))


def get_all_featured_media():
    with session_scope() as db_session:
        media = db_session.query(FeatureMediumORM).all()
        db_session.expunge_all()
    return media


def get_featured_media(condition):
    featured_media = get_all_featured_media()
    behaviors = set()
    species = set()
    perch_mount_names = set()
    for medium in featured_media:
        behaviors.add(medium.behavior)
        species.add(medium.species)
        perch_mount_names.add(medium.perch_mount_name)

    start_date = condition["start_date"] if condition["start_date"] else "2000-01-01"
    end_date = condition["end_date"] if condition["end_date"] else "2050-12-31"
    species = condition["species"] if condition["species"] else list(species)
    behaviors = condition["behaviors"] if condition["behaviors"] else list(behaviors)
    perch_mount_names = (
        condition["perch_mount_name"]
        if condition["perch_mount_name"]
        else list(perch_mount_names)
    )
    start_date = datetime.strptime(start_date, DATE_FROMAT)
    end_date = datetime.strptime(end_date, DATE_FROMAT)

    if "None" in species:
        condition = and_(
            FeatureMediumORM.medium_datetime >= start_date,
            FeatureMediumORM.medium_datetime <= end_date,
            or_(
                FeatureMediumORM.species.in_(species),
                FeatureMediumORM.species.is_(None),
            ),
            FeatureMediumORM.behavior.in_(behaviors),
            FeatureMediumORM.perch_mount_name.in_(perch_mount_names),
        )
    else:
        condition = and_(
            FeatureMediumORM.medium_datetime >= start_date,
            FeatureMediumORM.medium_datetime <= end_date,
            FeatureMediumORM.species.in_(species),
            FeatureMediumORM.behavior.in_(behaviors),
            FeatureMediumORM.perch_mount_name.in_(perch_mount_names),
        )

    with session_scope() as db_session:
        media = (
            db_session.query(FeatureMediumORM, MemberORM)
            .filter(condition)
            .outerjoin(MemberORM, MemberORM.member_id == FeatureMediumORM.featured_by)
            .order_by(desc(FeatureMediumORM.medium_datetime))
            .all()
        )
        # media = db_session.execute(
        #     select(
        #         FeatureMediumORM.title,
        #         FeatureMediumORM.description,
        #         FeatureMediumORM.medium_datetime,
        #         FeatureMediumORM.object_id,
        #         FeatureMediumORM.perch_mount_name,
        #         FeatureMediumORM.species,
        #         FeatureMediumORM.behavior,
        #         MemberORM.first_name,
        #         MemberORM.user_name,
        #     )
        #     .outerjoin(MemberORM, MemberORM.member_id == FeatureMediumORM.featured_by)
        #     .filter(condition)
        #     .order_by(desc(FeatureMediumORM.medium_datetime))
        # )

        db_session.expunge_all()

    return media


def get_num_unreviewed_media() -> int:
    with session_scope() as db_session:
        query = (
            db_session.query(func.count(distinct(tuple_(DetectedMediumORM.object_id))))
            .filter(DetectedMediumORM.reviewed == 0)
            .scalar()
        )
    return query


def get_num_unempty_check_media() -> int:
    with session_scope() as db_session:
        query = (
            db_session.query(func.count(distinct(tuple_(EmptyMediumORM.object_id))))
            .filter(EmptyMediumORM.empty_checked == 0)
            .scalar()
        )
    return query


def insert_detected_media(media):
    new_occurrences = []
    for medium in media:
        new_occurrence = DetectedMediumORM(
            taxon_order_by_ai=35133,
            medium_datetime=medium["medium_datetime"],
            medium_date=medium["medium_date"],
            object_id=medium["object_id"],
            perch_mount_name=medium["perch_mount_name"],
            perch_mount_id=medium["perch_mount_id"],
        )
        new_occurrences.append(new_occurrence)

    with session_scope() as db_session:
        db_session.add_all(new_occurrences)
        db_session.commit()


def insert_perch_mount(variable_table):
    layer = None if "layer" not in variable_table else variable_table["project_id"]
    new_perch_mount = PerchMountORM(
        perch_mount_name=variable_table["perch_mount_name"],
        latitude=variable_table["latitude"],
        longitude=variable_table["longitude"],
        habitat_id=variable_table["habitat_id"],
        project_id=variable_table["project_id"],
        layer=layer,
    )
    with session_scope() as db_session:
        db_session.add(new_perch_mount)
        db_session.commit()


def insert_member(member_form):
    new_member = MemberORM(
        user_name=member_form.user_name.data,
        first_name=member_form.first_name.data,
        last_name=member_form.last_name.data,
        phone_number=None
        if not member_form.phone_number.data
        else member_form.phone_number.data,
        email=None if not member_form.email.data else member_form.email.data,
        position_id=member_form.position_id.data,
    )
    with session_scope() as db_session:
        db_session.add(new_member)
        db_session.commit()


def insert_behavior(behavior_form):
    new_behavior = BehaviourORM(
        behavior_ch_name=behavior_form.behavior_ch_name.data,
        behavior_eng_name=behavior_form.behavior_eng_name.data,
    )

    with session_scope() as db_session:
        db_session.add(new_behavior)
        db_session.commit()


def insert_prey(prey_form):
    new_prey = PreyORM(
        prey_ch_name=prey_form.prey_ch_name.data,
        prey_eng_name=prey_form.prey_eng_name.data,
    )
    with session_scope() as db_session:
        db_session.add(new_prey)
        db_session.commit()


def insert_camera(camera_from):
    new_camera = CameraORM(camera_name=camera_from.camera_name.data)
    with session_scope() as db_session:
        db_session.add(new_camera)
        db_session.commit()


def insert_event(event_form):
    new_event = EventORM(
        event_ch_name=event_form.event_ch_name.data,
        event_eng_name=event_form.event_eng_name.data,
    )
    with session_scope() as db_session:
        db_session.add(new_event)
        db_session.commit()


def insert_feature_media(feature_media, perch_mount_name):
    new_media = []
    for medium in feature_media:
        new_medium = FeatureMediumORM(
            title=medium["title"],
            description=medium["description"],
            behavior=medium["behavior"],
            species=medium["species"],
            medium_datetime=medium["medium_datetime"],
            is_image=1 if medium["is_image"] else 0,
            object_id=medium["object_id"],
            perch_mount_name=perch_mount_name,
            featured_by=medium["featured_by"],
        )
        new_media.append(new_medium)
    with session_scope() as db_session:
        db_session.add_all(new_media)
        db_session.commit()


def insert_project(project_form):
    new_project = ProjectORM(project_name=project_form.project_name.data)
    with session_scope() as db_session:
        db_session.add(new_project)
        db_session.commit()


def update_perch_mount_status(perch_mount_id, status: int):
    with session_scope() as db_session:
        db_session.query(PerchMountORM).filter(
            PerchMountORM.perch_mount_id == perch_mount_id
        ).update({"terminated": status})
        db_session.commit()


def update_check_media(object_ids: list):
    with session_scope() as db_session:
        db_session.query(EmptyMediumORM).filter(
            EmptyMediumORM.object_id.in_(object_ids)
        ).update({"empty_checked": 1})
        db_session.commit()


def update_user(member_id: int, email: str, admin: bool, position_id: int):
    with session_scope() as db_session:
        db_session.query(MemberORM).filter(MemberORM.member_id == member_id).update(
            {
                "email": email,
                "admin": admin,
                "position_id": position_id,
            }
        )
        db_session.commit()


def update_perch_mount_claim(perch_mount_id: int, member_id: int):
    with session_scope() as db_session:
        db_session.query(PerchMountORM).filter(
            PerchMountORM.perch_mount_id == perch_mount_id
        ).update({"claim_by": member_id})
        db_session.commit()


def update_perch_mount_priority(perch_mount_id: int, priority: bool):
    with session_scope() as db_session:
        db_session.query(PerchMountORM).filter(
            PerchMountORM.perch_mount_id == perch_mount_id
        ).update({"is_priority": 1 if priority else 0})
        db_session.commit()


def reviewed_detected_media(object_ids: list):
    with session_scope() as db_session:
        db_session.query(DetectedMediumORM).filter(
            DetectedMediumORM.object_id.in_(object_ids)
        ).update({"reviewed": 1})
        db_session.commit()


def delete_detected_media_by_ids(object_ids):
    with session_scope() as db_session:
        db_session.query(DetectedMediumORM).filter(
            DetectedMediumORM.object_id.in_(object_ids)
        ).delete()
        db_session.commit()


def delete_featured_medium(feature_medium_id: int):
    with session_scope() as db_session:
        db_session.query(FeatureMediumORM).filter(
            FeatureMediumORM.feature_medium_id == feature_medium_id
        ).delete()
        db_session.commit()


if __name__ == "__main__":
    output = get_num_unreviewed_media()
    print(output)
