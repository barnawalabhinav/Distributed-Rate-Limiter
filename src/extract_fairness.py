import glob

PATH = "../data/*csv"
accepted_reqs = 0
refuted_reqs = 0
for file in glob.glob(PATH):
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            if 'accepted' in line:
                accepted_reqs += 1
            else:
                refuted_reqs += 1
