def heuristic_algorithm(file_path):
    import csv

    def heuristic_algorithm_0(file_path):
        # read data and store the information into your self-defined variables
        fp = open(file_path, "r", newline="")
        header = fp.readline()
        reader = csv.reader(fp, delimiter=",")

        info = []
        for row in reader:
            info.append(row)
        job_num = len(info)

        # start your algorithm here
        machine = []
        completion_time = []

        # The job and which machine it can use
        job_mac_1 = {}
        job_mac_2 = {}

        # Process the original data
        mac = []
        adj_info = []
        unused_info = []  # [stage1, stage2, due, num]
        num_list = []
        startTime = []
        non_list = []
        for i in range(job_num):
            job = info[i]
            job[0], job[5] = int(job[0]), float(job[5])
            job[1], job[2] = float(job[1]), float(job[2])
            job[3], job[4] = job[3].split(","), job[4].split(",")
            job_mac_1[i + 1] = job[3]
            job_mac_2[i + 1] = job[4] if job[4] != ["N/A"] else job[3]
            num_list.append(i + 1)
            startTime.append([])
            non_list.append([])

            # Find the set of machine
            for j in list(set(job[3])):
                if j not in mac:
                    mac.append(j)
            for j in list(set(job[4])):
                if j not in mac:
                    mac.append(j)
            if "N/A" in mac:
                mac.remove("N/A")

            # Sorting rule: working ratio, leisure gap
            ratio = (job[1] + job[2]) / job[-1]
            gap = job[-1] - job[1] - job[2]
            ratio_list = [(-1) * ratio, gap, job[1], job[2], job[5], job[0]]
            adj_info.append(ratio_list)
        adj_info.sort()

        # Some of the jobs has no flexibility
        while True:
            if adj_info[0][0] <= -0.9:
                adj_info[0].pop(0)
                adj_info[0].pop(0)
                adj_info[0][0], adj_info[0][1] = (-1) * \
                    adj_info[0][0], (-1)*adj_info[0][1]
                unused_info.append(adj_info[0])
                adj_info.pop(0)
            else:
                break

        # The set of jobs will be always tardy
        if unused_info != []:
            unused_info.sort()
            for i in range(len(unused_info)):
                unused_info[i][0] = unused_info[i][0] * (-1)
                unused_info[i][1] = unused_info[i][1] * (-1)

        # Some jobs has few flexibility need to process early
        bigsize_0 = []
        r = -0.75
        while True:
            if adj_info[0][0] <= r:
                bigsize_0.append(adj_info[0])
                adj_info.pop(0)
            else:
                break

        # A dict record the start time of working
        job_startTime = dict(zip(num_list, startTime))

        # A dict record the job and its machine
        job_m = dict(zip(num_list, non_list))

        # A dict represent the relation between erery machine and its time
        mac_num = []
        for i in range(len(mac)):
            mac_num.append(0)
        machine_dict = dict(zip(mac, mac_num))

        # If a job only has one working stage, turn it to stage two
        for i in adj_info:
            if i[3] == 0:
                i[3] = i[2]
                i[2] = 0
        for i in bigsize_0:
            if i[3] == 0:
                i[3] = i[2]
                i[2] = 0
        for i in unused_info:
            if i[1] == 0:
                i[1] = i[0]
                i[0] = 0

        # Create some interval of ratio (big)
        a = -0.9
        length = 3
        interval = []
        for i in range(length + 1):
            interval.append(a)
            a += 0.05

        temp_info = []
        for i in range(length):
            upper, lower = interval[i], interval[i + 1]
            temp = []
            k = 0
            for j in range(k, len(bigsize_0)):
                if upper <= bigsize_0[j][0] and lower >= bigsize_0[j][0]:
                    bigsize_0[j].pop(0)
                    temp.append(bigsize_0[j])
                    k += 1
                else:
                    continue
            temp_info.append(temp)

        # Sorting within an interval according to leisure gap
        bigsize = []
        for i in temp_info:
            if i != []:
                i.sort()
                for j in range(len(i)):
                    i[j].pop(0)
                    bigsize.append(i[j])

        # Create some interval of ratio (normal)
        a = r
        length = 15
        interval = []
        for i in range(length + 1):
            interval.append(a)
            a -= r / length

        temp_info = []
        for i in range(length):
            upper, lower = interval[i], interval[i + 1]
            temp = []
            k = 0
            for j in range(k, len(adj_info)):
                if upper <= adj_info[j][0] and lower >= adj_info[j][0]:
                    adj_info[j].pop(0)
                    temp.append(adj_info[j])
                    k += 1
                else:
                    continue
            temp_info.append(temp)

        # Sorting within an interval according to leisure gap
        final_info = []
        for i in temp_info:
            if i != []:
                i.sort()
                for j in range(len(i)):
                    i[j].pop(0)
                    final_info.append(i[j])

        # Process the bigsize
        for i in range(len(bigsize)):
            job = bigsize[i]
            can_use = job_mac_1[job[-1]]
            # print(job)

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()
            target = new_list[0][1]
            job_startTime[job[-1]].append(machine_dict[target])
            job_m[job[-1]].append(target)
            machine_dict[target] += job[0]

        # Some jobs' stage two will be tardy
        s2_unused = []
        for i in range(len(bigsize)):
            job = bigsize[i]
            can_use = job_mac_2[job[-1]]
            s1endTime = job_startTime[job[-1]][0] + job[0]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()

            for k in range(len(new_list)):
                target = new_list[k][1]
                end = machine_dict[target] + job[1]
                if end > job[-2]:
                    s2_unused.append(job)
                    break
                else:
                    if machine_dict[target] >= s1endTime:
                        job_startTime[job[-1]].append(machine_dict[target])
                        job_m[job[-1]].append(target)
                        machine_dict[target] += job[1]
                        break
                    else:
                        if k == len(new_list) - 1:
                            s2_unused.append(job)

        # Stage 1 of normal jobs
        for i in range(len(final_info)):
            job = final_info[i]
            can_use = job_mac_1[job[-1]]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()
            target = new_list[0][1]
            job_startTime[job[-1]].append(machine_dict[target])
            job_m[job[-1]].append(target)
            machine_dict[target] += job[0]

        # Stage 2 of normal jobs
        for i in range(len(final_info)):
            job = final_info[i]
            can_use = job_mac_2[job[-1]]
            s1endTime = job_startTime[job[-1]][0] + job[0]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()

            for k in range(len(new_list)):
                target = new_list[k][1]
                end = machine_dict[target] + job[1]
                if end > job[-2]:
                    s2_unused.append(job)
                    break
                else:
                    if machine_dict[target] >= s1endTime:
                        job_startTime[job[-1]].append(machine_dict[target])
                        job_m[job[-1]].append(target)
                        machine_dict[target] += job[1]
                        break
                    else:
                        if k == len(new_list) - 1:
                            s2_unused.append(job)

        # Stage 1 of unused
        if len(unused_info) != 0:
            for i in range(len(unused_info)):
                job = unused_info[i]
                can_use = job_mac_1[job[-1]]

                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()
                target = new_list[0][1]
                job_startTime[job[-1]].append(machine_dict[target])
                job_m[job[-1]].append(target)
                machine_dict[target] += job[0]

        s2_remains = []
        for i in range(len(unused_info)):
            a = unused_info[i]
            s2_remains.append([a[1], a[0], a[3]])
        for i in range(len(s2_unused)):
            a = s2_unused[i]
            s2_remains.append([a[1], a[0], a[3]])
        s2_remains.sort(reverse=True)

        for i in range(len(info)):
            job = info[i]
            if job[2] == 0:
                job_startTime[job[0]][0] = 0

        # Stage 2 of unused
        for i in range(len(s2_remains)):
            job = s2_remains[i]
            can_use = job_mac_2[job[-1]]
            s1endTime = job_startTime[job[-1]][0] + job[1]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()

            for k in range(len(new_list)):
                target = new_list[k][1]
                if machine_dict[target] >= s1endTime:
                    job_startTime[job[-1]].append(machine_dict[target])
                    job_m[job[-1]].append(target)
                    machine_dict[target] += job[0]
                    break

        # Few jobs violating the rule will have errors
        check = []
        startTime = sorted(list(job_startTime.items()))
        for i in startTime:
            if len(i[1]) == 1:
                check.append(i)

        if len(check) != 0:
            for i in range(len(check)):
                item = check[i]
                jobNum = item[0]
                s1endTime = item[1][0] + info[jobNum-1][1]
                can_use = job_mac_2[jobNum]

                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()

                target = new_list[0][1]
                job_startTime[jobNum].append(s1endTime)
                job_m[jobNum].append(target)
                machine_dict[target] = s1endTime + info[jobNum-1][2]

        times = list(machine_dict.values())
        times.sort(reverse=True)

        # List "completion_time"
        temp_time = sorted(list(job_startTime.items()))
        for i in range(len(temp_time)):
            completion_time.append(temp_time[i][1])
        for i in range(len(completion_time)):
            if info[i][2] != 0:
                completion_time[i][0] += info[i][1]
                completion_time[i][0] = round(completion_time[i][0], 5)
                completion_time[i][1] += info[i][2]
                completion_time[i][1] = round(completion_time[i][1], 5)
            else:
                completion_time[i][0] += info[i][2]
                completion_time[i][0] = round(completion_time[i][0], 5)
                completion_time[i][1] += info[i][1]
                completion_time[i][1] = round(completion_time[i][1], 5)

        for i in range(len(info)):
            if info[i][2] == 0:
                completion_time[i][0] = completion_time[i][1]

        # Minimize the makespan
        while True:
            s1e = ms = idx = 0
            for i in range(len(completion_time)):
                if completion_time[i][1] > ms and info[i][2] != 0:
                    s1e = completion_time[i][0]
                    ms = completion_time[i][1]
                    idx = i + 1

            if idx > 0:
                can_use = job_mac_2[idx]
                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()
                t, m = new_list[0][0], new_list[0][1]

                if s1e > t and s1e != (ms - info[idx-1][2]):
                    completion_time[idx-1][1] = s1e + info[idx-1][2]
                    job_m[idx][1] = m
                    machine_dict[m] = completion_time[idx-1][1]
                else:
                    break

        makespan = 0
        for i in completion_time:
            if i[1] > makespan:
                makespan = i[1]
        makespan = round(makespan, 3)

        # List "machine"
        m_list = sorted(job_m.items())
        for i in range(len(m_list)):
            machine.append(m_list[i][1])
        for i in range(len(info)):
            if info[i][2] == 0:
                machine[i][0] = (machine[i][1])
                machine[i][1] = -1
        for i in range(len(machine)):
            machine[i][0] = int(machine[i][0])
            machine[i][1] = int(machine[i][1])

        tardy = 0
        for i in range(len(completion_time)):
            if completion_time[i][1] > info[i][-1]:
                tardy += 1

        return machine, completion_time, tardy, makespan

    def heuristic_algorithm_1(file_path):
        # read data and store the information into your self-defined variables
        fp = open(file_path, "r", newline="")
        header = fp.readline()
        reader = csv.reader(fp, delimiter=",")

        info = []
        for row in reader:
            info.append(row)
        job_num = len(info)

        # start your algorithm here
        machine = []
        completion_time = []

        # The job and which machine it can use
        job_mac_1 = {}
        job_mac_2 = {}

        # Process the original data
        mac = []
        adj_info = []
        unused_info = []  # [stage1, stage2, due, num]
        num_list = []
        startTime = []
        non_list = []
        for i in range(job_num):
            job = info[i]
            job[0], job[5] = int(job[0]), float(job[5])
            job[1], job[2] = float(job[1]), float(job[2])
            job[3], job[4] = job[3].split(","), job[4].split(",")
            job_mac_1[i + 1] = job[3]
            job_mac_2[i + 1] = job[4] if job[4] != ["N/A"] else job[3]
            num_list.append(i + 1)
            startTime.append([])
            non_list.append([])

            # Find the set of machine
            for j in list(set(job[3])):
                if j not in mac:
                    mac.append(j)
            for j in list(set(job[4])):
                if j not in mac:
                    mac.append(j)
            if "N/A" in mac:
                mac.remove("N/A")

            # Sorting rule: working ratio, leisure gap
            ratio = (job[1] + job[2]) / job[-1]
            gap = job[-1] - job[1] - job[2]
            ratio_list = [(-1) * ratio, gap, job[1], job[2], job[5], job[0]]
            adj_info.append(ratio_list)
        adj_info.sort()

        # Some of the jobs has no flexibility
        while True:
            if adj_info[0][0] <= -1:
                adj_info[0].pop(0)
                adj_info[0].pop(0)
                adj_info[0][0], adj_info[0][1] = (-1) * \
                    adj_info[0][0], (-1)*adj_info[0][1]
                unused_info.append(adj_info[0])
                adj_info.pop(0)
            else:
                break
        # The set of jobs will be always tardy
        if unused_info != []:
            unused_info.sort()
            for i in range(len(unused_info)):
                unused_info[i][0] = unused_info[i][0] * (-1)
                unused_info[i][1] = unused_info[i][1] * (-1)

        # A dict record the start time of working
        job_startTime = dict(zip(num_list, startTime))

        # A dict record the job and its machine
        job_m = dict(zip(num_list, non_list))

        # A dict represent the relation between erery machine and its time
        mac_num = []
        for i in range(len(mac)):
            mac_num.append(0)
        machine_dict = dict(zip(mac, mac_num))

        # If a job only has one working stage, turn it to stage two
        for i in adj_info:
            if i[3] == 0:
                i[3] = i[2]
                i[2] = 0

        # Create some interval of ratio
        a = -1
        length = 20
        interval = []
        for i in range(length + 1):
            interval.append(a)
            a += 0.05

        temp_info = []
        for i in range(length):
            upper, lower = interval[i], interval[i + 1]
            temp = []
            k = 0
            for j in range(k, len(adj_info)):
                if upper <= adj_info[j][0] and lower >= adj_info[j][0]:
                    adj_info[j].pop(0)
                    temp.append(adj_info[j])
                    k += 1
                else:
                    continue
            temp_info.append(temp)

        # Sorting within an interval according to leisure gap
        final_info = []
        for i in temp_info:
            if i != []:
                i.sort()
                for j in range(len(i)):
                    i[j].pop(0)
                    final_info.append(i[j])

        s2_unused = []
        # Stage 1 of normal jobs
        for i in range(len(final_info)):
            job = final_info[i]
            can_use = job_mac_1[job[-1]]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()
            target = new_list[0][1]
            job_startTime[job[-1]].append(machine_dict[target])
            job_m[job[-1]].append(target)
            machine_dict[target] += job[0]

        # Stage 2 of normal jobs
        for i in range(len(final_info)):
            job = final_info[i]
            can_use = job_mac_2[job[-1]]
            s1endTime = job_startTime[job[-1]][0] + job[0]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()

            for k in range(len(new_list)):
                target = new_list[k][1]
                end = machine_dict[target] + job[1]
                if end > job[-2]:
                    s2_unused.append(job)
                    break
                else:
                    if machine_dict[target] >= s1endTime:
                        job_startTime[job[-1]].append(machine_dict[target])
                        job_m[job[-1]].append(target)
                        machine_dict[target] += job[1]
                        break
                    else:
                        if k == len(new_list) - 1:
                            s2_unused.append(job)

        # Stage 1 of unused
        if len(unused_info) != 0:
            for i in range(len(unused_info)):
                job = unused_info[i]
                can_use = job_mac_1[job[-1]]

                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()
                target = new_list[0][1]
                job_startTime[job[-1]].append(machine_dict[target])
                job_m[job[-1]].append(target)
                machine_dict[target] += job[0]

        s2_remains = []
        for i in range(len(unused_info)):
            a = unused_info[i]
            s2_remains.append([a[1], a[0], a[3]])
        for i in range(len(s2_unused)):
            a = s2_unused[i]
            s2_remains.append([a[1], a[0], a[3]])
        s2_remains.sort(reverse=True)

        for i in range(len(info)):
            job = info[i]
            if job[2] == 0:
                job_startTime[job[0]][0] = 0

        # Stage 2 of unused
        for i in range(len(s2_remains)):
            job = s2_remains[i]
            can_use = job_mac_2[job[-1]]
            s1endTime = job_startTime[job[-1]][0] + job[1]

            new_list = []
            for j in can_use:
                new_list.append([machine_dict[j], j])
            new_list.sort()

            for k in range(len(new_list)):
                target = new_list[k][1]
                if machine_dict[target] >= s1endTime:
                    job_startTime[job[-1]].append(machine_dict[target])
                    job_m[job[-1]].append(target)
                    machine_dict[target] += job[0]
                    break

        # Few jobs violating the rule will have errors
        check = []
        startTime = sorted(list(job_startTime.items()))
        for i in startTime:
            if len(i[1]) == 1:
                check.append(i)

        if len(check) != 0:
            for i in range(len(check)):
                item = check[i]
                jobNum = item[0]
                s1endTime = item[1][0] + info[jobNum-1][1]
                can_use = job_mac_2[jobNum]

                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()

                target = new_list[0][1]
                job_startTime[jobNum].append(s1endTime)
                job_m[jobNum].append(target)
                machine_dict[target] = s1endTime + info[jobNum-1][2]

        times = list(machine_dict.values())
        times.sort(reverse=True)

        # List "completion_time"
        temp_time = sorted(list(job_startTime.items()))
        for i in range(len(temp_time)):
            completion_time.append(temp_time[i][1])
        for i in range(len(completion_time)):
            if info[i][2] != 0:
                completion_time[i][0] += info[i][1]
                completion_time[i][0] = round(completion_time[i][0], 5)
                completion_time[i][1] += info[i][2]
                completion_time[i][1] = round(completion_time[i][1], 5)
            else:
                completion_time[i][0] += info[i][2]
                completion_time[i][0] = round(completion_time[i][0], 5)
                completion_time[i][1] += info[i][1]
                completion_time[i][1] = round(completion_time[i][1], 5)

        for i in range(len(info)):
            if info[i][2] == 0:
                completion_time[i][0] = completion_time[i][1]

        # Minimize the makespan
        while True:
            s1e = ms = idx = 0
            for i in range(len(completion_time)):
                if completion_time[i][1] > ms and info[i][2] != 0:
                    s1e = completion_time[i][0]
                    ms = completion_time[i][1]
                    idx = i + 1

            if idx > 0:
                can_use = job_mac_2[idx]
                new_list = []
                for j in can_use:
                    new_list.append([machine_dict[j], j])
                new_list.sort()
                t, m = new_list[0][0], new_list[0][1]

                if s1e > t and s1e != (ms - info[idx-1][2]):
                    completion_time[idx-1][1] = s1e + info[idx-1][2]
                    job_m[idx][1] = m
                    machine_dict[m] = completion_time[idx-1][1]
                else:
                    break

        makespan = 0
        for i in completion_time:
            if i[1] > makespan:
                makespan = i[1]
        makespan = round(makespan, 3)

        # List "machine"
        m_list = sorted(job_m.items())
        for i in range(len(m_list)):
            machine.append(m_list[i][1])
        for i in range(len(info)):
            if info[i][2] == 0:
                machine[i][0] = (machine[i][1])
                machine[i][1] = -1
        for i in range(len(machine)):
            machine[i][0] = int(machine[i][0])
            machine[i][1] = int(machine[i][1])

        tardy = 0
        for i in range(len(completion_time)):
            if completion_time[i][1] > info[i][-1]:
                tardy += 1

        return machine, completion_time, tardy, makespan

    m1, c1, t1, ms1 = heuristic_algorithm_0(file_path)
    m2, c2, t2, ms2 = heuristic_algorithm_1(file_path)
    if t1 < t2:
        machine, completion_time = m1, c1
    elif t1 > t2:
        machine, completion_time = m2, c2
    else:
        if ms1 <= ms2:
            machine, completion_time = m1, c1
        else:
            machine, completion_time = m2, c2

    return machine, completion_time
