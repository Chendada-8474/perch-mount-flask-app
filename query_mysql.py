import os
import yaml
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base

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
)

Base = declarative_base()
Base.metadata.reflect(engine)
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


def get_full_table(table_orm):
    table = db_session.query(table_orm).all()
    return table


def get_perch_mount_names():
    perch_mount_names = db_session.query(PerchMountORM.perch_mount_name).all()
    return [name[0] for name in perch_mount_names]


def get_perch_mounts():
    perch_mount = (
        db_session.query(PerchMountORM, HabitatORM)
        .join(HabitatORM, PerchMountORM.habitat_id == HabitatORM.habitat_id)
        .all()
    )
    return perch_mount


def get_behaviors():
    behaviors = db_session.query(BehaviourORM).all()
    return behaviors


def get_members():
    members = (
        db_session.query(MemberORM, PositionORM)
        .join(PositionORM, PositionORM.position_id == MemberORM.position_id)
        .all()
    )
    return members


def get_cameras():
    cameras = db_session.query(CameraORM).order_by(CameraORM.camera_id).all()
    return cameras


def get_preys():
    preys = db_session.query(PreyORM).all()
    return preys


def get_positions():
    positions = db_session.query(PositionORM).all()
    return positions


def get_habitats():
    habitats = db_session.query(HabitatORM).all()
    return habitats


def get_projects():
    project = db_session.query(ProjectORM).all()
    return project


def get_habitat_by_id(habitat_id):
    habitat = (
        db_session.query(HabitatORM).filter(HabitatORM.habitat_id == habitat_id).one()
    )
    return habitat


def get_id_by_perch_mount_name(perch_mount_name: str):
    perch_mount_id = (
        db_session.query(PerchMountORM.perch_mount_id)
        .filter(PerchMountORM.perch_mount_name == perch_mount_name)
        .one()
    )
    return perch_mount_id[0]


def get_projects_by_id(project_ids):
    project = (
        db_session.query(ProjectORM)
        .filter(ProjectORM.project_id.in_(project_ids))
        .all()
    )
    return project


def insert_perch_mount(perch_mount_form):
    new_perch_mount = PerchMountORM(
        perch_mount_name=perch_mount_form.perch_mount_name.data,
        latitude=perch_mount_form.latitude.data,
        longitude=perch_mount_form.longitude.data,
        habitat_id=perch_mount_form.habitat_id.data,
    )

    db_session.add(new_perch_mount)
    db_session.commit()

    perch_mount_id = db_session.query(PerchMountORM.perch_mount_id).filter(
        PerchMountORM.perch_mount_name == perch_mount_form.perch_mount_name.data
    )
    new_perch_mount_project = [
        PerchMountProjectORM(perch_mount_id=perch_mount_id, project_id=project_id)
        for project_id in perch_mount_form.project_id.data
    ]
    db_session.add_all(new_perch_mount_project)
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
    db_session.add(new_member)
    db_session.commit()


def insert_behavior(behavior_form):
    new_behavior = BehaviourORM(
        behavior_ch_name=behavior_form.behavior_ch_name.data,
        behavior_eng_name=behavior_form.behavior_eng_name.data,
    )
    db_session.add(new_behavior)
    db_session.commit()


def insert_prey(prey_form):
    new_prey = PreyORM(
        prey_ch_name=prey_form.prey_ch_name.data,
        prey_eng_name=prey_form.prey_eng_name.data,
    )
    db_session.add(new_prey)
    db_session.commit()


def insert_camera(camera_from):
    new_camera = CameraORM(camera_name=camera_from.camera_name.data)
    db_session.add(new_camera)
    db_session.commit()


if __name__ == "__main__":
    print(get_id_by_perch_mount_name("九地樹林"))
