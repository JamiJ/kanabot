import sqlite3
from os.path import isfile
from sqlite3 import connect
from apscheduler.triggers.cron import CronTrigger # pylint: disable=import-error

DB_PATH = "./data/db/database.db"
BUILD_PATH = "./data/db/build.sql"

cxn = connect(DB_PATH, check_same_thread=False)
cur = cxn.cursor()


def with_commit(func):
	def inner(*args, **kwargs):
		func(*args, **kwargs)
		commit()

	return inner

@with_commit
def build():
	if isfile(BUILD_PATH):
		scriptexec(BUILD_PATH)

def commit():
	print("commiting...")
	cxn.commit()

def autosave(sched):
	sched.add_job(commit, CronTrigger(second=0))
#second=0 = every minute
#minute=0 = every hour	

def close():
	cxn.close()


def field(command, *values):
	cur.execute(command, tuple(values))

	if (fetch := cur.fetchone()) is not None:
		return fetch[0]


def record(command, *values):
	cur.execute(command, tuple(values))

	return cur.fetchone()


def records(command, *values):
	cur.execute(command, tuple(values))

	return cur.fetchall()


def column(command, *values):
	cur.execute(command, tuple(values))

	return [Item[0] for item in cur.fetchall()]


def execute(command, *values):
	cur.execute(command, tuple(values))


def multiexec(command, valueset):
	cur.executemany(command, valueset)


def scriptexec(path):
	with open(path, "r", encoding="utf-8") as script:
		cur.executescript(script.read())