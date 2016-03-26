# Built for Python 3 >= 3.4.0. Despite my best efforts to write portable code,
# it's not gonna be tested on python2.

# Usage pattern: "python validator.py <.json file name> <.json file name>..."

import sys
import json
import hashlib
import logging
import time

logging.basicConfig(level=logging.DEBUG)

def json_str_tests(json_string, filename):
    def traverse_all_tasks(tasklist, callback, filename):
        for task in tasklist:
            callback(task, filename)
            traverse_all_tasks(task["subtasks"], callback, filename)

    def req_obj_test(motherdict, filename):
        # Every required object and no extras included
        def req_callback(task, filename):
            allset = set(["task-weight", "name", "progress",
                         "deadline", "subtasks", "creation-timestamp"])
            if allset != set(task):
                logging.error("Object list isn't pure, object\n%s", task)
        if (not "version" in motherdict) or (not "extra" in motherdict):
            logging.error("Object list isn't pure, motherdict of %s", filename)
        traverse_all_tasks(motherdict['tasks'], req_callback, filename)

    def check_times(motherdict, filename):
        # time is in the same, UTC-aligned format
        def times_callback(task, filename):
            try:
                if task["deadline"] is not None:
                    time.strptime(task["deadline"], "%Y-%m-%dT%H:%M:%SZ")
                time.strptime(task["creation-timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                logging.error("Time errors out: %s in %s", task,
                              filename)
        traverse_all_tasks(motherdict['tasks'], times_callback, filename)

    def check_version(motherdict, filename):
        # Version is known to server
        if motherdict['version'] != 1:
            logging.error("Unsupported file version in %s", filename)
    
    def composite_test(motherdict, filename):
        # Composite weights form 100%
        # Composite names all check out
        # composite has at least 2 subtasks
        def comp_callback(task, filename):
            subtasks = task["subtasks"]
            subtweights = task["task-weight"]
            if task['progress'] == "composite":
                if len(subtasks) < 2:
                    logging.error("Composite with <2 tasks doesn't make sense")
                subtnames = [x["name"] for x in subtasks]
                if set(subtweights) != set(subtnames):
                    logging.error("Composite weights aren't the same list"
                                  " as subtasks, %s %s", filename, task)
                if sum(subtweights.values()) != 1:
                    logging.error("Composite weights don't form 100%")
            else:
                if subtweights:
                    logging.error("Subtasks should not have weights if nocomp")

        traverse_all_tasks(motherdict['tasks'], comp_callback, filename)

    def check_progress(motherdict, filename):
        # progress 0 < x < 1
        def prog_callback(task, filename):
            if task["progress"] != str:
                if not (0 < task["progress"] < 1):
                    logging.error("Progress value not in bounds! %s %s", 
                                  filename, task)
            elif task["progress"] != "composite":
                logging.error("Progress value is an unknown string!")

        traverse_all_tasks(motherdict['tasks'], prog_callback, filename)

    motherdict = json.loads(json_string)

    req_obj_test(motherdict, filename)
    check_times(motherdict, filename)
    check_version(motherdict, filename)
    composite_test(motherdict, filename)
    check_progress(motherdict, filename)

    
def parent_test(json_string, old_json_string):
    # Not implemented until server is, but basic idea:
    # your sha-prev is equal to the parent's sha256, and
    # you BOTH pass shatest
    pass

def validate(json_string, filename):
    shatest(json_string, filename)
    json_str_tests(json_string, filename)


if __name__ == "__main__":
    for fname in sys.argv[1:]:
        with open(fname) as f:
            fstring = f.read()
        validate(fstring, fname)
