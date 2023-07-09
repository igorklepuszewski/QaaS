import os
from dotenv import load_dotenv, find_dotenv


def export_envs(filepath):
    load_dotenv(find_dotenv())

