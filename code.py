import random


minutes = 300
self_reports_count = 15
S_threshold = 0.5
Zs = [random.randint(0, 1) for i in range(minutes)]
Rs = {i * 20 - random.randint(0, 5): random.randint(0, 1) for i in range(1, self_reports_count + 1)}
Pr_Z = {
    0: len([Z for Z in Zs if Z == 0]) / len(Zs),
    1: len([Z for Z in Zs if Z == 1]) / len(Zs)
}

# assumption 1 : all matching R&Z are exceptions
best_alpha = None
best_beta = None
grid_step_size = 1
comb_f1_scores = []
for alpha in [x / 10 for x in range(0, 11, grid_step_size)]:
    for beta in [x / 10 for x in range(0, 11, grid_step_size)]:
        Ss = {i+1: Rs[i] for i in Rs if Rs[i] == Zs[i]}
        tps, fps, fns = 0, 0, 0

        # compute perceived stress
        for i in range(1, minutes):
            if i not in Ss and i-1 in Ss:
                if Ss[i - 1] == Zs[i - 1]:
                    # i-1 : S=0, Z=0 or S=1, Z=1
                    Ss[i] = Ss[i - 1]  # 0/1  i.e. exception cases
                elif Ss[i - 1] > S_threshold:
                    # i-1 : S=1, Z=0
                    Ss[i] = alpha * (1 - Pr_Z[Zs[i - 1]]) + Pr_Z[Zs[i - 1]]
                elif Ss[i - 1] <= S_threshold:
                    # i-1 : S=0, Z=1
                    Ss[i] = beta * Pr_Z[Zs[i - 1]]
            # compute conf mtx data
            if i in Rs and Rs[i] != Zs[i]:
                if i in Ss:
                    if Ss[i] >= 0.5 and Rs[i] == 1:
                        tps += 1
                    elif Ss[i] >= 0.5 and Rs[i] == 0:
                        fps += 1
                    elif Ss[i] < 0.5 and Rs[i] == 1:
                        fns += 1

        # compute F1 score
        f1_denom = tps + 1 / 2 * (fps + fns)
        f1_score = str(tps / f1_denom) if f1_denom != 0 else '-'
        comb_f1_scores += [(alpha, beta, f1_score, Ss)]


# assumption 2 : only first R&Z is an exception
# todo fill


# log results
with open('res.csv', 'w+') as w:
    w.write(f'Pr(Z=1)={Pr_Z[1]}, Pr(Z=0)={Pr_Z[0]}\n')
    # log Z, S, R
    w.write(f',,,,,Z,{",".join([str(x) for x in Zs])}\n')
    w.write(f',,,,,R,{",".join([str(Rs[i]) if i in Rs else "-" for i in range(minutes)])}\n')
    w.write('alpha,beta,f1_score,,,S\n')
    for alpha, beta, f1_score, Ss in comb_f1_scores:
        w.write(f'{alpha},{beta},{f1_score},,,,{",".join([f"{Ss[i]:0.02f}" if i in Ss else "-" for i in range(minutes)])}\n')
