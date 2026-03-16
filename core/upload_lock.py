import os

LOCK_DIR="locks"

os.makedirs(LOCK_DIR,exist_ok=True)

def acquire_lock(npsn):

    path=f"{LOCK_DIR}/{npsn}.lock"

    if os.path.exists(path):
        return False

    open(path,"w").close()

    return True


def release_lock(npsn):

    path=f"{LOCK_DIR}/{npsn}.lock"

    if os.path.exists(path):
        os.remove(path)