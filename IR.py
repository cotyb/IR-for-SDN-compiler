import fsm
import SA
import pickle
import os

Merlin_sa_path = "./Merlin_sa/"
SNAP_sa_path = "./SNAP_sa/"

def load_pickle(f):
    f = open(f, "r")
    res = pickle.loads(f.read())
    f.close()
    return res


if __name__ == "__main__":
    files = os.listdir(Merlin_sa_path)
    Merlin_all_sa = []
    for file in files:
        Merlin_all_sa.append(load_pickle(Merlin_sa_path + file))
    SNAP_sa = load_pickle(SNAP_sa_path + "SNAP_sa")
    print SNAP_sa.to_fsm()




