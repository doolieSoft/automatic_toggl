import os

if __name__ == "__main__":
    root_rapport = "C:\\Users\\c158492\\ProjetBoulot\\PYTHON\\automatic_toggl\\rapport\\"
    first_report_name = root_rapport + "rapport-2022-06-01.csv"

    output = open("chargement_2022-09-19.csv", mode="w", encoding="utf8")

    i = 0
    for file in os.listdir(root_rapport):
        if root_rapport + file < first_report_name or not file.endswith(".csv"):
            continue


        with open(root_rapport + file, mode="r", encoding="utf8") as current_file:
            j = 0
            for line in current_file:
                if i == 0:
                    output.write(line)
                    print(line.strip("\n"))
                else:
                    if j > 0:
                        output.write(line)
                        print(line.strip("\n"))
                j += 1
            i += 1
