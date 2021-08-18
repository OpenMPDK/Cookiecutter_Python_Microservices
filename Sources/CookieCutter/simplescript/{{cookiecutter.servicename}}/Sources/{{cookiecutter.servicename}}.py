import logging

"""
__main__
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting {{cookiecutter.servicename}}")

    logging.info("{{cookiecutter.servicename}} has finished executing")