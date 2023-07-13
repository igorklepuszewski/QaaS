import os

from dotenv import find_dotenv, load_dotenv


def export_envs(filepath):
    load_dotenv(find_dotenv())
