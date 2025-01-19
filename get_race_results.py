import module.get_race_result

if __name__ == '__main__':
    with open("./OUTPUT/race_result_urls.csv") as fr:
        while(True):
            line = fr.readline().replace("\n", "")
            if not line:
                break
            print(module.get_race_result.get_race_result(line))